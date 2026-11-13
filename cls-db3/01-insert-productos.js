// Producto U2 — bases de datos III
// Script 01: carga inicial de documentos en MongoDB
// Base: ingeniar_inoxidable | coleccion: catalogo_productos

// Cambia (o crea, si no existe) la base de datos
use("ingeniar_inoxidable");

// Insercion de los 10 documentos de prueba
db.catalogo_productos.insertMany([
  {
    "_id": "PROD-INOX-001",
    "nombre_producto": "Mesa de Trabajo Sanitaria en Acero 304",
    "categoria": "Mobiliario Industrial",
    "tipo_acero": "AISI 304",
    "precio_base_estimado": 1850000,
    "tiempo_estandar_minutos": 240,
    "es_personalizado": true,
    "etapas_proceso": ["Corte Laser", "Plegado", "Soldadura TIG", "Pulido Sanitario"],
    "insumos_requeridos": [
      { "material": "Lámina Calibre 16", "cantidad": 1.5, "unidad": "Lámina" }
    ],
    "disponible_entrega_rapida": false
  },
  {
    "_id": "PROD-INOX-002",
    "nombre_producto": "Tanque Mezclador de 500L con Agitador",
    "categoria": "Tanques y Recipientes",
    "tipo_acero": "AISI 316L",
    "precio_base_estimado": 12500000,
    "tiempo_estandar_minutos": 720,
    "es_personalizado": true,
    "etapas_proceso": ["Corte Laser", "Rolinado", "Soldadura TIG", "Ensamble Mecanico", "Prueba Hidrostatica"],
    "insumos_requeridos": [
      { "material": "Lámina 3mm 316L", "cantidad": 4, "unidad": "Lámina" }
    ],
    "disponible_entrega_rapida": false
  },
  {
    "_id": "PROD-INOX-003",
    "nombre_producto": "Estante Modular Calibre 18",
    "categoria": "Almacenamiento",
    "tipo_acero": "AISI 430",
    "precio_base_estimado": 650000,
    "tiempo_estandar_minutos": 90,
    "es_personalizado": false,
    "etapas_proceso": ["Punzonado", "Plegado", "Pintura Electrostatica", "Ensamble"],
    "insumos_requeridos": [
      { "material": "Lámina Calibre 18", "cantidad": 2, "unidad": "Lámina" }
    ],
    "disponible_entrega_rapida": true
  },
  {
    "_id": "PROD-INOX-004",
    "nombre_producto": "Pasamanos Arquitectónico con Conectores",
    "categoria": "Arquitectura y Construccion",
    "tipo_acero": "AISI 304",
    "precio_base_estimado": 450000,
    "tiempo_estandar_minutos": 120,
    "es_personalizado": true,
    "etapas_proceso": ["Corte Sierra", "Soldadura TIG", "Pulido Espejo"],
    "insumos_requeridos": [
      { "material": "Tubo Redondo 2 pulgadas", "cantidad": 6, "unidad": "Metros" }
    ],
    "disponible_entrega_rapida": true
  },
  {
    "_id": "PROD-INOX-005",
    "nombre_producto": "Campana Extractora de Humos 2 Metros",
    "categoria": "Ventilacion Industrial",
    "tipo_acero": "AISI 304",
    "precio_base_estimado": 2800000,
    "tiempo_estandar_minutos": 300,
    "es_personalizado": true,
    "etapas_proceso": ["Corte Laser", "Plegado", "Remachado", "Ensamble"],
    "insumos_requeridos": [
      { "material": "Lámina Calibre 20", "cantidad": 3, "unidad": "Lámina" }
    ],
    "disponible_entrega_rapida": false
  },
  {
    "_id": "PROD-INOX-006",
    "nombre_producto": "Fregadero Industrial de 2 Pocetas",
    "categoria": "Mobiliario Industrial",
    "tipo_acero": "AISI 304",
    "precio_base_estimado": 1200000,
    "tiempo_estandar_minutos": 180,
    "es_personalizado": false,
    "etapas_proceso": ["Embutido", "Soldadura TIG", "Pulido Sanitario"],
    "insumos_requeridos": [
      { "material": "Lámina Calibre 16", "cantidad": 1, "unidad": "Lámina" }
    ],
    "disponible_entrega_rapida": true
  },
  {
    "_id": "PROD-INOX-007",
    "nombre_producto": "Mezclador de Polvos Tipo Cinta (Ribbon Blender)",
    "categoria": "Maquinaria Especializada",
    "tipo_acero": "AISI 316L",
    "precio_base_estimado": 18000000,
    "tiempo_estandar_minutos": 960,
    "es_personalizado": true,
    "etapas_proceso": ["Corte Laser", "Mecanizado CNC", "Soldadura TIG", "Balanceo", "Prueba Electrica"],
    "insumos_requeridos": [
      { "material": "Eje Macizo 2 pulgadas", "cantidad": 2, "unidad": "Metros" }
    ],
    "disponible_entrega_rapida": false
  },
  {
    "_id": "PROD-INOX-008",
    "nombre_producto": "Rejilla de Drenaje Sanitaria Reforzada",
    "categoria": "Arquitectura y Construccion",
    "tipo_acero": "AISI 304",
    "precio_base_estimado": 220000,
    "tiempo_estandar_minutos": 45,
    "es_personalizado": false,
    "etapas_proceso": ["Corte Laser", "Soldadura TIG"],
    "insumos_requeridos": [
      { "material": "Platina 3/16", "cantidad": 1, "unidad": "Metros" }
    ],
    "disponible_entrega_rapida": true
  },
  {
    "_id": "PROD-INOX-009",
    "nombre_producto": "Carro Bandejero para Horno Pastelería",
    "categoria": "Mobiliario Industrial",
    "tipo_acero": "AISI 430",
    "precio_base_estimado": 950000,
    "tiempo_estandar_minutos": 150,
    "es_personalizado": false,
    "etapas_proceso": ["Corte Sierra", "Soldadura MIG", "Ensamble"],
    "insumos_requeridos": [
      { "material": "Tubo Cuadrado 1 pulgada", "cantidad": 12, "unidad": "Metros" }
    ],
    "disponible_entrega_rapida": false
  },
  {
    "_id": "PROD-INOX-010",
    "nombre_producto": "Tolva de Recepción de Granos 1 Tonelada",
    "categoria": "Tanques y Recipientes",
    "tipo_acero": "AISI 304",
    "precio_base_estimado": 4200000,
    "tiempo_estandar_minutos": 420,
    "es_personalizado": true,
    "etapas_proceso": ["Corte Laser", "Plegado", "Soldadura TIG", "Pulido Comercial"],
    "insumos_requeridos": [
      { "material": "Lámina Calibre 14", "cantidad": 3, "unidad": "Lámina" }
    ],
    "disponible_entrega_rapida": false
  }
]);

// Confirmacion de la carga
print("Documentos insertados en catalogo_productos: " + db.catalogo_productos.countDocuments());