import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1 - Carga de datos
df = pd.read_csv("Colombianos_detenidos_en_el_exterior_20261006.csv", dtype=str)

# Limpiar nombres de columnas (quitar espacios)
df.columns = df.columns.str.strip()

print("Informacion inicial")
print(df.info())
print("\nPrimeras filas:")
print(df.head())
print("\nValores nulos por columna:")
print(df.isnull().sum())

# 2 - Limpieza de datos

# 2.1 - Eliminar duplicados
df = df.drop_duplicates()
print(f"\nRegistros despues de eliminar duplicados: {len(df)}")

# 2.2 - Tratar valores nulos
# Quita valores nulos en categorias para evitar errores
columnas_texto = ["PAIS PRISIÓN", "CONSULADO", "DELITO", 
                  "EXTRADITADO Y O REPATRIADO", "SITUACIÓN JURÍDICA", 
                  "GÉNERO", "GRUPO EDAD"]
for col in columnas_texto:
    if col in df.columns:
        df[col] = df[col].fillna("DESCONOCIDO")

# Rellena valores nulos en cantidad con 0 y converte tipo de dato a entero
df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(0).astype(int)

# Converte fecha de publicacion en datetime y elimina filas sin fecha
df["FECHA PUBLICACIÓN"] = pd.to_datetime(df["FECHA PUBLICACIÓN"], errors="coerce")
df = df.dropna(subset=["FECHA PUBLICACIÓN"])

# 2.3 - Limpieza de texto
for col in columnas_texto:
    if col in df.columns:
        df[col] = df[col].str.strip().str.upper()

# Quitar redundancias
df["PAIS PRISIÓN"] = df["PAIS PRISIÓN"].replace({
    "ESTADOS UNIDOS DE AMERICA": "ESTADOS UNIDOS",
    "MEXICO": "MÉXICO",
    "ESPANA": "ESPAÑA",
    "REPUBLICA DOMINICANA": "REPÚBLICA DOMINICANA",
    "PAISES BAJOS": "PAÍSES BAJOS",
    "REINO UNIDO": "REINO UNIDO",
    "COREA, REPUBLICA DE": "COREA DEL SUR",
    "FEDERACION DE RUSIA": "RUSIA",
    "TANZANIA, REPUBLICA UNIDA DE": "TANZANIA",
    "VIET NAM": "VIETNAM"
})

df["DELITO"] = df["DELITO"].replace({
    "NARCOTRAFICO": "NARCOTRÁFICO",
    "ROBO / HURTO": "ROBO/HURTO",
    "HOMICIDIO / TENTATIVA DE": "HOMICIDIO/TENTATIVA",
    "PORTE ILEGAL DE ARMAS": "PORTE ILEGAL DE ARMAS",
    "DELITO MIGRATORIO": "DELITO MIGRATORIO",
    "DELITOS SEXUALES": "DELITOS SEXUALES"
})

# 2.4 - Corregir inconcistencias en coordenadas
for col in ["LATITUD", "LONGITUD"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
        df[col] = pd.to_numeric(df[col], errors="coerce")

# 2.5 - Extraer año y mes de la fecha
df["AÑO"] = df["FECHA PUBLICACIÓN"].dt.year
df["MES"] = df["FECHA PUBLICACIÓN"].dt.month
df["NOMBRE_MES"] = df["FECHA PUBLICACIÓN"].dt.month_name()

# Verificar limpieza
print("\nDespues de la limpieza:")
print(df.info())
print("\nValores nulos restantes:")
print(df.isnull().sum())

# Guardar
df.to_csv("colombianos_detenidos_limpio.csv", index=False)
print("\nDataset limpio guardado como 'colombianos_detenidos_limpio.csv'")

# 3 - Agrupacion y analisis

print("\nAgrupaciones")

# 3.1 - Top 10 paises con mas detenidos
top_paises = df.groupby("PAIS PRISIÓN")["CANTIDAD"].sum().sort_values(ascending=False).head(10)
print("\nTop 10 paises con mas colombianos detenidos:")
print(top_paises)

# 3.2 - Top 10 delitos mas comunes
top_delitos = df.groupby("DELITO")["CANTIDAD"].sum().sort_values(ascending=False).head(10)
print("\nTop 10 delitos mas comunes:")
print(top_delitos)

# 3.3 - Distribucion por genero
genero = df.groupby("GÉNERO")["CANTIDAD"].sum()
print("\nDistribucion por genero:")
print(genero)

# 3.4 - Distribucion por edad
edad = df.groupby("GRUPO EDAD")["CANTIDAD"].sum().sort_values(ascending=False)
print("\nDistribucion por grupo de edad:")
print(edad)

# 3.5 - Detenidos por año
por_año = df.groupby("AÑO")["CANTIDAD"].sum()
print("\nDetenidos por año:")
print(por_año)

# 3.6 - Agrupación por país y delito
top5_paises = top_paises.index.tolist()
top5_delitos = top_delitos.index.tolist()
cruce = df[df["PAIS PRISIÓN"].isin(top5_paises) & df["DELITO"].isin(top5_delitos)]
cruce_group = cruce.groupby(["PAIS PRISIÓN", "DELITO"])["CANTIDAD"].sum().unstack(fill_value=0)
print("\nCruce pais vs delito (top 5):")
print(cruce_group)

# 4 - Visualización de datos

# 4.1 - Grafico de barras: Top 10 países
plt.figure(figsize=(12, 6))
sns.barplot(x=top_paises.values, y=top_paises.index, palette="viridis")
plt.title("Top 10 paises con mas colombianos detenidos", fontsize=16)
plt.xlabel("Cantidad de detenidos")
plt.ylabel("Pais")
plt.tight_layout()
plt.savefig("top_paises.png")
plt.show()

# 4.2 - Grafico de barras: Top 10 delitos
plt.figure(figsize=(12, 6))
sns.barplot(x=top_delitos.values, y=top_delitos.index, palette="magma")
plt.title("Top 10 delitos mas comunes", fontsize=16)
plt.xlabel("Cantidad de detenidos")
plt.ylabel("Delito")
plt.tight_layout()
plt.savefig("top_delitos.png")
plt.show()

# 4.3 - Grafico de pastel: Distribución por género
plt.figure(figsize=(8, 8))
plt.pie(genero.values, labels=genero.index, autopct="%1.1f%%", startangle=140, colors=sns.color_palette("pastel"))
plt.title("Distribucion por genero", fontsize=16)
plt.savefig("genero.png")
plt.show()

# 4.4 - Grafico de barras: Grupo de edad
plt.figure(figsize=(10, 6))
sns.barplot(x=edad.index, y=edad.values, palette="coolwarm")
plt.title("Distribucion por grupo de edad", fontsize=16)
plt.xlabel("Grupo de edad")
plt.ylabel("Cantidad")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("grupo_edad.png")
plt.show()

# 4.5 - Evolucion temporal por año
plt.figure(figsize=(12, 6))
sns.lineplot(x=por_año.index, y=por_año.values, marker="o", color="b")
plt.title("Evolucion de detenciones por año", fontsize=16)
plt.xlabel("Año")
plt.ylabel("Cantidad de detenidos")
plt.grid(True)
plt.tight_layout()
plt.savefig("evolucion_anual.png")
plt.show()

# 4.6 - Mapa de calor: Pais vs Delito
plt.figure(figsize=(12, 8))
sns.heatmap(cruce_group, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5)
plt.title("Cruce Pais vs Delito (Top 5)", fontsize=16)
plt.xlabel("Delito")
plt.ylabel("Pais")
plt.tight_layout()
plt.savefig("heatmap_pais_delito.png")
plt.show()