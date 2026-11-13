// Script 02: Consultas find, update y delete
// Base: ingeniar_inoxidable | Coleccion: catalogo_productos

use("ingeniar_inoxidable");

// Consulta 1 — Igualdad
// Pregunta que productos son de acero AISI 316L
db.catalogo_productos.find({ tipo_acero: "AISI 316L" }).pretty();

// CONSULTA 2 — Comparacion con $gt
// Pregunta que productos cuestan mas de $2.000.000
db.catalogo_productos.find({ precio_base_estimado: { $gt: 2000000 } }).pretty();

// CONSULTA 3 — Lista de opciones con $in
// Pregunta que productos son de mobiliario industrial o tanques y recipientes
db.catalogo_productos.find({
  categoria: { $in: ["Mobiliario Industrial", "Tanques y Recipientes"] }
}).pretty();

// Consulta 4 — Busqueda dentro de un arreglo
// Pregunta que productos incluyen soldadura TIG en sus etapas
db.catalogo_productos.find({ etapas_proceso: "Soldadura TIG" }).pretty();

// Update — Actualizar el precio de PROD-INOX-003
// Como el acero subio, actualiza el precio a 720000
// Precio antes
db.catalogo_productos.findOne({ _id: "PROD-INOX-003" });

db.catalogo_productos.updateOne(
  { _id: "PROD-INOX-003" },
  { $set: { precio_base_estimado: 720000 } }
);

// Precio despues
db.catalogo_productos.findOne({ _id: "PROD-INOX-003" });

// Delete — Eliminar PROD-INOX-008
// Como la rejilla de drenaje ya no se fabrica, se elimina
// Conteo antes
db.catalogo_productos.countDocuments();

db.catalogo_productos.deleteOne({ _id: "PROD-INOX-008" });

// Conteo despues
db.catalogo_productos.countDocuments();