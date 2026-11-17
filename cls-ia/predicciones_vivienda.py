"""Proyecciones de hogares. Lee el CSV limpio sin modificarlo.

Ejemplo dentro del contenedor:
python3 predicciones_vivienda.py --archivo Subsidios_De_Vivienda_Limpio.csv
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

ANIO = "Año de Asignación"
HOGARES = "Hogares"
CODIGO = "Código Divipola Municipio"


def cargar(archivo):
    df = pd.read_csv(archivo, encoding="utf-8-sig", dtype={CODIGO: "string"})
    necesarias = {ANIO, HOGARES, CODIGO, "Programa", "Estado de Postulación"}
    if necesarias - set(df.columns):
        raise ValueError(f"Faltan columnas: {sorted(necesarias - set(df.columns))}")
    for columna in [ANIO, HOGARES]:
        # Conversión en memoria para calcular; no se escribe sobre el archivo.
        df[columna] = pd.to_numeric(df[columna], errors="raise")
        if df[columna].isna().any() or not np.isfinite(df[columna]).all():
            raise ValueError(f"Hay valores vacíos o no finitos en {columna}.")
        if (df[columna] % 1 != 0).any():
            raise ValueError(f"Se esperaban enteros en {columna}.")
    if (df[HOGARES] < 0).any():
        raise ValueError("Hay cantidades negativas de hogares.")
    return df


def agrupar(df):
    # Un año sin registros no se transforma automáticamente en cero.
    return df.groupby(ANIO, as_index=False)[HOGARES].sum().sort_values(ANIO)


def evaluar(serie, etiqueta):
    """Predice los últimos tres años observados usando solo años anteriores."""
    filas = []
    for i in range(max(2, len(serie) - 3), len(serie)):
        entrenamiento = serie.iloc[:i]
        prueba = serie.iloc[[i]]
        modelo = LinearRegression().fit(entrenamiento[[ANIO]], entrenamiento[HOGARES])
        filas.append({
            "Serie": etiqueta,
            ANIO: int(prueba[ANIO].iloc[0]),
            "Hogares observados": int(prueba[HOGARES].iloc[0]),
            "Prediccion lineal": float(modelo.predict(prueba[[ANIO]])[0]),
            "Referencia ultimo anio observado": int(entrenamiento[HOGARES].iloc[-1]),
        })
    return filas


def proyectar(serie, anios, etiqueta):
    if len(serie) < 2:
        return pd.DataFrame()
    modelo = LinearRegression().fit(serie[[ANIO]], serie[HOGARES])
    futuro = pd.DataFrame({ANIO: anios})
    valores = modelo.predict(futuro)
    futuro["Serie"] = etiqueta
    futuro["Hogares estimados"] = np.rint(valores).astype(int)
    # Se conserva el resultado del modelo para que un valor negativo sea visible.
    futuro["Advertencia"] = np.where(
        valores < 0, "Prediccion negativa: no interpretable como hogares", ""
    )
    return futuro


def graficar(serie, futuro, titulo, archivo):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(serie[ANIO], serie[HOGARES], "o-", label="Historico")
    ax.plot(futuro[ANIO], futuro["Hogares estimados"], "o--", label="Proyeccion lineal")
    ax.set(xlabel="Año de asignación", ylabel="Suma de hogares", title=titulo)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(archivo, dpi=160)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archivo", type=Path, required=True)
    parser.add_argument("--salida", type=Path, default=Path("resultados_predicciones"))
    parser.add_argument("--ultimo-anio-completo", type=int, default=2025)
    parser.add_argument("--municipio", default="66001", help="Código Divipola; 66001 es Pereira")
    args = parser.parse_args()
    entrada = args.archivo.resolve()
    salida = args.salida.resolve()
    if salida == entrada or entrada in salida.parents:
        raise ValueError("La salida debe ser una carpeta distinta del CSV de entrada.")
    df = cargar(entrada)
    historico = df[df[ANIO] <= args.ultimo_anio_completo].copy()
    nacional = agrupar(historico)
    if len(nacional) < 2:
        raise ValueError("Se necesitan al menos dos años históricos para entrenar.")
    if int(nacional[ANIO].max()) != args.ultimo_anio_completo:
        raise ValueError("El último año completo indicado no tiene registros.")
    salida.mkdir(parents=True, exist_ok=True)
    anios = list(range(args.ultimo_anio_completo + 1, args.ultimo_anio_completo + 11))
    print(f"Filas leídas: {len(df):,}. Filas usadas hasta {args.ultimo_anio_completo}: {len(historico):,}.")
    print("Se conservan las filas repetidas y se incluyen TODOS los estados de postulación.")
    print("La variable estimada es la suma de Hogares de los registros; no hogares únicos ni subsidios vigentes.")
    print("2026 se excluye del entrenamiento por ser un año parcial en este archivo.")
    proyecciones = []
    evaluaciones = []
    omitidas = []
    series = [("General", nacional),
              (f"Municipio {args.municipio}", agrupar(historico[historico[CODIGO] == args.municipio]))]
    series.extend((f"Programa: {nombre}", agrupar(grupo))
                  for nombre, grupo in historico.groupby("Programa"))
    for etiqueta, serie in series:
        if len(serie) < 2:
            omitidas.append({"Serie": etiqueta, "Motivo": "Menos de dos años observados"})
            continue
        prediccion = proyectar(serie, anios, etiqueta)
        prediccion["Ultimo anio observado"] = int(serie[ANIO].max())
        proyecciones.append(prediccion)
        evaluaciones.extend(evaluar(serie, etiqueta))
        if etiqueta == "General" or etiqueta.startswith("Municipio "):
            nombre = "general" if etiqueta == "General" else f"municipio_{args.municipio}"
            graficar(serie, prediccion, etiqueta, salida / f"{nombre}.png")
    resultados = pd.concat(proyecciones, ignore_index=True)
    resultados.to_csv(salida / "predicciones_10_anios.csv", index=False, encoding="utf-8-sig")
    resultados[resultados[ANIO] == 2027].to_csv(
        salida / "predicciones_2027.csv", index=False, encoding="utf-8-sig")
    nacional.to_csv(salida / "historico_general.csv", index=False, encoding="utf-8-sig")
    if evaluaciones:
        detalle = pd.DataFrame(evaluaciones)
        detalle.to_csv(salida / "evaluacion_detalle.csv", index=False, encoding="utf-8-sig")
        resumen = []
        for etiqueta, grupo in detalle.groupby("Serie"):
            mae = mean_absolute_error(grupo["Hogares observados"], grupo["Prediccion lineal"])
            referencia = mean_absolute_error(grupo["Hogares observados"], grupo["Referencia ultimo anio observado"])
            resumen.append({"Serie": etiqueta, "Anios evaluados": len(grupo),
                            "MAE lineal": mae, "MAE referencia": referencia,
                            "Lineal mejora referencia": mae < referencia})
        pd.DataFrame(resumen).to_csv(salida / "evaluacion_resumen.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(omitidas, columns=["Serie", "Motivo"]).to_csv(
        salida / "series_omitidas.csv", index=False, encoding="utf-8-sig")
    print("\nProyecciones para 2027:")
    print(resultados[resultados[ANIO] == 2027].to_string(index=False))
    print(f"\nResultados guardados en: {salida}")
    print("Las proyecciones a diez años extrapolan una tendencia; no incorporan cambios de política o presupuesto.")
    print("Los programas se modelan por separado: sus proyecciones no tienen por qué sumar la general.")


if __name__ == "__main__":
    main()
