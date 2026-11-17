import pandas as pd

datos = {
    'Nombre': ['Ana', 'Carlos', 'Luisa', 'Juan', 'Sofia'],
    'Edad': [20, 22, 21, 23, 20],
    'Nota 1': [4.5, 3.2, 4.8, 2.9, 4.0],
    'Nota 2': [3.8, 3.5, 4.6, 3.0, 3.9],
    'Nota 3': [4.2, 3.8, 4.9, 3.2, 4.1],
    'Ciudad': ['Bogota', 'Medellin', 'Cali', 'Barranquilla', 'Bogota']
}

df = pd.DataFrame(datos)

print("DataFrame original")
print(df)
print("\n")

df['Promedio'] = (df['Nota 1'] + df['Nota 2'] + df['Nota 3']) / 3
df['Promedio'] = df['Promedio'].round(2)

print("Nota promedio de cada estudiante")
print(df[['Nombre', 'Promedio']])
print("\n")

df['Estado'] = df['Promedio'].apply(lambda x: 'Aprobado' if x >= 3.5 else 'Reprobado')

print("Estado de cada estudiante")
print(df[['Nombre', 'Promedio', 'Estado']])
print("\n")

estudiantes_bogota = df[df['Ciudad'] == 'Bogota']

print("Estudiantes de Bogota")
print(estudiantes_bogota[['Nombre', 'Ciudad', 'Promedio']])
print("\n")

indice_mejor = df['Promedio'].idxmax()
mejor_estudiante = df.loc[indice_mejor]

print("Estudiante con la mejor nota promedio")
print(f"El mejor estudiante es {mejor_estudiante['Nombre']} con un promedio de {mejor_estudiante['Promedio']}")
print("\n")

df.to_excel("estudiantes_notas.xlsx", index=False)
print("Archivo excel guardado correctamente como 'estudiantes_notas.xlsx' en la carpeta actual.")