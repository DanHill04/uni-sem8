"""Proyecto final de Bases de Datos III: Ingeniar Inoxidable.

Originalmente se ejecuta dentro de un contenedor Docker con MongoDB y Redis, pero 
puede probarse localmente.

Comandos iniciales:
    - export MONGO_URL='mongodb://localhost:27017'
    - python3 -m uvicorn main:app --app-dir /workspace/cls-db3/api_inox --host 0.0.0.0 --port 8000

"""

import json
import os
import re
from contextlib import asynccontextmanager
from threading import RLock
from typing import Annotated

import redis
from fastapi import FastAPI, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError, PyMongoError


# Un solo reporte, con una clave que sigue tipo:entidad:id.
CACHE_REPORTE = "cache:reporte:entrega_rapida_por_categoria"
PATRON_ID = r"PROD-INOX-[0-9]{3}"
Texto = Annotated[str, Field(min_length=1, max_length=150)]
Precio = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Minutos = Annotated[int, Field(gt=0)]
Etapas = Annotated[list[Texto], Field(min_length=1, max_length=30)]


# MODELOS
class ModeloEstricto(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
    )


class Insumo(ModeloEstricto):
    material: Texto
    cantidad: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    unidad: Annotated[str, Field(min_length=1, max_length=40)]


Insumos = Annotated[list[Insumo], Field(min_length=1, max_length=50)]

EJEMPLO_PRODUCTO = {
    "_id": "PROD-INOX-099",
    "nombre_producto": "Mesa de Prueba para Cotizaciones",
    "categoria": "Mobiliario Industrial",
    "tipo_acero": "AISI 304",
    "precio_base_estimado": 1500000,
    "tiempo_estandar_minutos": 180,
    "es_personalizado": True,
    "etapas_proceso": ["Corte Laser", "Plegado", "Soldadura TIG"],
    "insumos_requeridos": [
        {"material": "Lamina Calibre 16", "cantidad": 1.5, "unidad": "Lamina"}
    ],
    "disponible_entrega_rapida": True,
}


class ProductoCrear(ModeloEstricto):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
        json_schema_extra={"examples": [EJEMPLO_PRODUCTO]},
    )
    id: str = Field(alias="_id", pattern="^" + PATRON_ID + "$", max_length=13)
    nombre_producto: Texto
    categoria: Annotated[str, Field(min_length=1, max_length=100)]
    tipo_acero: Annotated[str, Field(min_length=1, max_length=30)]
    precio_base_estimado: Precio
    tiempo_estandar_minutos: Minutos
    es_personalizado: bool
    etapas_proceso: Etapas
    insumos_requeridos: Insumos
    disponible_entrega_rapida: bool


class ProductoActualizar(ModeloEstricto):
    """PUT parcial: solo se modifican los campos enviados; el ID no cambia."""

    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
        allow_inf_nan=False,
        json_schema_extra={
            "examples": [{"precio_base_estimado": 1600000, "disponible_entrega_rapida": False}]
        },
    )
    nombre_producto: Texto | None = None
    categoria: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    tipo_acero: Annotated[str, Field(min_length=1, max_length=30)] | None = None
    precio_base_estimado: Precio | None = None
    tiempo_estandar_minutos: Minutos | None = None
    es_personalizado: bool | None = None
    etapas_proceso: Etapas | None = None
    insumos_requeridos: Insumos | None = None
    disponible_entrega_rapida: bool | None = None

    @model_validator(mode="after")
    def validar_campos_enviados(self):
        if not self.model_fields_set:
            raise ValueError("Envia al menos un campo para actualizar.")
        for campo in self.model_fields_set:
            if getattr(self, campo) is None:
                raise ValueError("Los campos enviados no pueden ser null: " + campo)
        return self


# CONEXIONES
@asynccontextmanager
async def lifespan(app: FastAPI):
    missing = [name for name in ("MONGO_URL", "REDIS_URL") if not os.getenv(name)]
    if missing:
        raise RuntimeError("Faltan variables de entorno: " + ", ".join(missing))
    try:
        ttl = int(os.getenv("CACHE_TTL_SEGUNDOS", "120"))
        if ttl < 1:
            raise ValueError
    except ValueError:
        raise RuntimeError("CACHE_TTL_SEGUNDOS debe ser un entero mayor que cero.") from None

    mongo = MongoClient(
        os.environ["MONGO_URL"],
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
    )
    try:
        cliente_redis = redis.Redis.from_url(
            os.environ["REDIS_URL"],
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        try:
            app.state.mongo = mongo
            app.state.db = mongo[os.getenv("MONGO_DB", "ingeniar_inoxidable")]
            app.state.redis = cliente_redis
            app.state.cache_ttl = ttl
            app.state.cache_segura = True
            # Coordina cambios y reportes concurrentes en este proceso Uvicorn.
            app.state.reporte_lock = RLock()
            yield
        finally:
            cliente_redis.close()
    finally:
        mongo.close()


app = FastAPI(
    title="Ingeniar Inoxidable - Bases de Datos III",
    description=(
        "Catalogo de productos en MongoDB, reporte con cache en Redis "
        "e invalidacion al crear, actualizar o eliminar, y contador de visitas."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# FUNCIONES COMPARTIDAS
def validar_id_producto(producto_id: str) -> str:
    if re.fullmatch(PATRON_ID, producto_id) is None:
        raise HTTPException(400, "Formato de identificador invalido. Usa PROD-INOX-001.")
    return producto_id


def buscar_producto(request: Request, producto_id: str) -> dict:
    validar_id_producto(producto_id)
    try:
        producto = request.app.state.db.catalogo_productos.find_one({"_id": producto_id})
    except PyMongoError:
        raise HTTPException(503, "No se pudo consultar el catalogo en MongoDB.") from None
    if producto is None:
        raise HTTPException(404, "Producto no encontrado.")
    return producto


def invalidar_cache(request: Request, producto_eliminado: str | None = None) -> bool:
    """Se llama despues de cada escritura exitosa, dentro de reporte_lock."""
    estado = request.app.state
    estado.cache_segura = False
    claves = [CACHE_REPORTE]
    if producto_eliminado is not None:
        claves.append("visitas:producto:" + producto_eliminado)
    try:
        estado.redis.delete(*claves)
    except redis.exceptions.RedisError:
       
        return False
    estado.cache_segura = True
    return True


# ESTADO DE LAS BASES
@app.get(
    "/ping", tags=["Estado"], summary="Comprobar MongoDB y Redis",
    responses={503: {"description": "Una o ambas bases no responden"}},
)
def ping(request: Request, response: Response):
    mongo_ok = False
    redis_ok = False
    try:
        mongo_ok = request.app.state.mongo.admin.command("ping")["ok"] == 1
    except PyMongoError:
        pass
    try:
        redis_ok = bool(request.app.state.redis.ping())
    except redis.exceptions.RedisError:
        pass
    if not (mongo_ok and redis_ok):
        response.status_code = 503
    return {
        "estado": "ok" if mongo_ok and redis_ok else "error",
        "mongo_responde": mongo_ok,
        "redis_responde": redis_ok,
    }


# CRUD EN MONGODB
@app.get("/productos", tags=["Productos"], summary="Listar productos con filtros y limite")
def listar_productos(
    request: Request,
    categoria: str | None = Query(default=None, min_length=1, max_length=100),
    tipo_acero: str | None = Query(default=None, min_length=1, max_length=30),
    disponible_entrega_rapida: bool | None = None,
    limite: int = Query(default=10, ge=1, le=100),
):
    filtro = {}
    if categoria is not None:
        filtro["categoria"] = categoria
    if tipo_acero is not None:
        filtro["tipo_acero"] = tipo_acero
    if disponible_entrega_rapida is not None:
        filtro["disponible_entrega_rapida"] = disponible_entrega_rapida
    try:
        productos = list(
            request.app.state.db.catalogo_productos.find(filtro).sort("_id", 1).limit(limite)
        )
    except PyMongoError:
        raise HTTPException(503, "No se pudo consultar el catalogo en MongoDB.") from None
    return {"total_mostrados": len(productos), "limite": limite, "productos": productos}


@app.get(
    "/productos/{producto_id}", tags=["Productos"], summary="Consultar un producto por ID",
    responses={400: {"description": "ID invalido"}, 404: {"description": "No existe"}},
)
def obtener_producto(producto_id: str, request: Request):
    return buscar_producto(request, producto_id)


@app.post(
    "/productos", tags=["Productos"], summary="Crear un producto validado",
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "El identificador ya existe"}},
)
def crear_producto(datos: ProductoCrear, request: Request):
    documento = datos.model_dump(by_alias=True)
    
    with request.app.state.reporte_lock:
        try:
            request.app.state.db.catalogo_productos.insert_one(documento)
        except DuplicateKeyError:
            raise HTTPException(409, "Ya existe un producto con ese identificador.") from None
        except PyMongoError:
            raise HTTPException(503, "No se pudo crear el producto en MongoDB.") from None
        cache_invalidada = invalidar_cache(request)
    return {
        "mensaje": "Producto creado.",
        "producto": documento,
        "cache_invalidada": cache_invalidada,
    }


@app.put(
    "/productos/{producto_id}", tags=["Productos"],
    summary="Actualizar uno o varios campos de un producto",
    description="Envia solo los campos a modificar. No permite cambiar _id ni enviar null.",
    responses={400: {"description": "ID invalido"}, 404: {"description": "No existe"}},
)
def actualizar_producto(producto_id: str, datos: ProductoActualizar, request: Request):
    validar_id_producto(producto_id)
    cambios = datos.model_dump(exclude_unset=True)
    with request.app.state.reporte_lock:
        try:
            actualizado = request.app.state.db.catalogo_productos.find_one_and_update(
                {"_id": producto_id}, {"$set": cambios}, return_document=ReturnDocument.AFTER
            )
        except PyMongoError:
            raise HTTPException(503, "No se pudo actualizar el producto en MongoDB.") from None
        if actualizado is None:
            raise HTTPException(404, "Producto no encontrado.")
        cache_invalidada = invalidar_cache(request)
    return {
        "mensaje": "Producto actualizado.",
        "producto": actualizado,
        "cache_invalidada": cache_invalidada,
    }


@app.delete(
    "/productos/{producto_id}", tags=["Productos"], summary="Eliminar un producto",
    responses={400: {"description": "ID invalido"}, 404: {"description": "No existe"}},
)
def eliminar_producto(producto_id: str, request: Request):
    validar_id_producto(producto_id)
    with request.app.state.reporte_lock:
        try:
            resultado = request.app.state.db.catalogo_productos.delete_one({"_id": producto_id})
        except PyMongoError:
            raise HTTPException(503, "No se pudo eliminar el producto en MongoDB.") from None
        if resultado.deleted_count == 0:
            raise HTTPException(404, "Producto no encontrado.")
        cache_invalidada = invalidar_cache(request, producto_eliminado=producto_id)
    return {
        "mensaje": "Producto eliminado.",
        "id": producto_id,
        "cache_invalidada": cache_invalidada,
    }


# REPORTE
@app.get(
    "/reportes/entrega-rapida-por-categoria", tags=["Reportes"],
    summary="Cantidad de productos de entrega rapida por categoria",
)
def reporte_entrega_rapida(request: Request):
    estado = request.app.state
    with estado.reporte_lock:
        # 1. Buscar primero el reporte en Redis.
        if estado.cache_segura:
            try:
                guardado = estado.redis.get(CACHE_REPORTE)
                if guardado is not None:
                    datos = json.loads(guardado)
                    if not isinstance(datos, list) or not all(
                        isinstance(fila, dict)
                        and isinstance(fila.get("_id"), str)
                        and type(fila.get("cantidad_productos")) is int
                        and fila["cantidad_productos"] >= 0
                        for fila in datos
                    ):
                        raise ValueError("Formato de cache invalido")
                    return {
                        "origen": "redis", "datos": datos,
                        "ttl_segundos": max(0, estado.redis.ttl(CACHE_REPORTE)),
                        "cache_guardada": True,
                    }
            except (redis.exceptions.RedisError, ValueError, TypeError):
                # Cache ausente, inaccesible o corrupta: se consulta MongoDB.
                pass

        # 2. Ejecutar el pipeline sobre los datos principales.
        pipeline = [
            {"$match": {"disponible_entrega_rapida": True}},
            {"$group": {"_id": "$categoria", "cantidad_productos": {"$sum": 1}}},
            {"$sort": {"cantidad_productos": -1, "_id": 1}},
        ]
        try:
            datos = list(estado.db.catalogo_productos.aggregate(pipeline))
        except PyMongoError:
            raise HTTPException(503, "No se pudo generar el reporte en MongoDB.") from None

        # 3. Guardar el resultado con vencimiento para las siguientes consultas.
        cache_guardada = False
        try:
            estado.redis.set(CACHE_REPORTE, json.dumps(datos, ensure_ascii=False), ex=estado.cache_ttl)
            estado.cache_segura = True
            cache_guardada = True
        except redis.exceptions.RedisError:
            pass
        return {
            "origen": "mongo", "datos": datos,
            "ttl_segundos": estado.cache_ttl if cache_guardada else 0,
            "cache_guardada": cache_guardada,
        }


# SEGUNDO USO DE REDIS
@app.post(
    "/productos/{producto_id}/visitas", tags=["Visitas"],
    summary="Registrar una visita al producto",
    description="Metrica auxiliar sin vencimiento. No registra ventas ni cotizaciones.",
)
def registrar_visita(producto_id: str, request: Request):
    buscar_producto(request, producto_id)
    clave = "visitas:producto:" + producto_id
    try:
        total = request.app.state.redis.incr(clave)
    except redis.exceptions.RedisError:
        raise HTTPException(503, "No se pudo incrementar el contador en Redis.") from None
    return {"producto_id": producto_id, "visitas": total, "clave": clave}


@app.get(
    "/productos/{producto_id}/visitas", tags=["Visitas"],
    summary="Consultar las visitas del producto",
)
def consultar_visitas(producto_id: str, request: Request):
    buscar_producto(request, producto_id)
    clave = "visitas:producto:" + producto_id
    try:
        valor = request.app.state.redis.get(clave)
        total = int(valor) if valor is not None else 0
    except (redis.exceptions.RedisError, ValueError, TypeError):
        raise HTTPException(503, "No se pudo leer el contador en Redis.") from None
    return {"producto_id": producto_id, "visitas": total, "clave": clave}
