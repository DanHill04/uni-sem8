API DE INGENIAR INOXIDABLE
Proyecto final de Bases de Datos III

ENTORNO
Recordar que originalmente esta hecho para un contenedor en docker, por lo que
si se va a ejecutar fuera de dicho contenedor se debera de hacer la respectiva
configuracion.

Iniciar en el contenedor, fuera de mongosh:
  python3 -m uvicorn main:app --app-dir /workspace/cls-db3/api_inox --host 0.0.0.0 --port 8000

Desde Windows, abrir con HTTP:
  http://localhost:8000/docs

ENDPOINTS
GET    /ping
GET    /productos
GET    /productos/{producto_id}
POST   /productos
PUT    /productos/{producto_id}
DELETE /productos/{producto_id}
GET    /reportes/entrega-rapida-por-categoria
POST   /productos/{producto_id}/visitas
GET    /productos/{producto_id}/visitas

VALIDACIONES
ID: PROD-INOX- seguido de exactamente tres digitos.
Los ID son strings del proyecto, no ObjectId.
GET, PUT y DELETE devuelven 400 por ID con formato incorrecto y 404 si no existe.
POST usa un modelo validado, con _id en el JSON; devuelve 201 si crea
el producto, 409 si el ID ya existe y 422 por campos ausentes o invalidos.
PUT modifica solo los campos enviados. Rechaza un cuerpo vacio,
valores null, campos desconocidos y cambios de _id con 422.
Las listas de etapas e insumos deben contener al menos un elemento.
Los numeros deben ser positivos; los tipos no se convierten desde texto.
GET /productos admite categoria, tipo_acero, disponible_entrega_rapida
y limite entre 1 y 100. Los filtros de texto usan igualdad exacta.

REPORTE Y CACHE
Pregunta: cuantos productos disponibles para entrega rapida tiene cada
categoria, ordenados de mayor a menor cantidad.
Pipeline: $match, $group con $sum: 1 y $sort.
Clave: cache:reporte:entrega_rapida_por_categoria
Vencimiento por defecto: 120 segundos.
Primero busca en Redis; si falta, consulta Mongo y guarda el resultado.
La respuesta indica origen mongo o redis.
La creacion, actualizacion y eliminacion invalidan el reporte con delete.
El indicador cache_invalidada confirma si Redis recibio la invalidacion;
True tambien aplica si la clave no existia y por tanto no habia nada que borrar.
Si Mongo ya cambio y Redis falla al invalidar, la escritura se informa como
exitosa con cache_invalidada: false para evitar reintentos duplicados.
Este proceso deja de leer la cache hasta poder reemplazarla por un reporte nuevo.
Si Redis no responde, el reporte puede responder desde Mongo con
cache_guardada: false. /ping informa 503 si una base deja de responder.

VISITAS
Clave: visitas:producto:PROD-INOX-XXX
POST incrementa con INCR; GET devuelve el contador o cero si no existe.
El producto debe existir. El contador es una metrica auxiliar sin vencimiento.
Eliminar el producto tambien intenta borrar su contador.
El contador existente del Trabajo 1 se conserva: no siempre empezara en cero.

El Swagger incluye ejemplos listos para POST y PUT.
Los indices existentes no se borran ni se recrean al iniciar la API.