import csv
from pathlib import Path
from flask import Flask, abort, render_template, request

app = Flask(__name__)
DATA = Path(__file__).resolve().parent / "data"
MODULOS = {
    "historico": ("Datos históricos", "historico_general.csv", None),
    "general": ("Predicción general", "predicciones_10_anios.csv", "general.png"),
    "pereira": ("Pereira", "predicciones_10_anios.csv", "municipio_66001.png"),
    "programas": ("Programas de vivienda", "predicciones_10_anios.csv", None),
    "evaluacion": ("Evaluación del modelo", "evaluacion_resumen.csv", None),
}


@app.route("/")
def introduccion():
    return render_template("introduccion.html", activo="introduccion")


@app.route("/modulo/<nombre>")
def modulo(nombre):

    if nombre not in MODULOS:
        abort(404)
    titulo, archivo, imagen = MODULOS[nombre]

    try:

        with (DATA / archivo).open(encoding="utf-8-sig", newline="") as fuente:
            lector = csv.DictReader(fuente)
            columnas, filas = lector.fieldnames or [], list(lector)

    except FileNotFoundError:

        return render_template("modulo.html", activo=nombre, titulo=titulo,
                               error=f"Copia {archivo} en la carpeta data."), 503
    programas, seleccionado = [], ""

    if nombre in ("general", "pereira"):

        serie = "General" if nombre == "general" else "Municipio 66001"
        filas = [fila for fila in filas if fila["Serie"] == serie]

    elif nombre == "programas":

        programas = sorted({fila["Serie"] for fila in filas if fila["Serie"].startswith("Programa: ")})
        seleccionado = request.args.get("programa", programas[0] if programas else "")

        if seleccionado and seleccionado not in programas:

            abort(400, description="Programa no disponible.")
        filas = [fila for fila in filas if fila["Serie"] == seleccionado]
        
    return render_template("modulo.html", activo=nombre, titulo=titulo, error=None,
                           columnas=columnas, filas=filas, imagen=imagen,
                           programas=programas, seleccionado=seleccionado)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
