import pandas as pd

temperaturas_pereira = pd.Series(
    [22, 24, 19, 21, 25, 23, 20],
    index=['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
)

print("Temperaturas de la semana:")
print(temperaturas_pereira)

#Temperatura del miercoles (por nombre)
print("\nTemperatura del miercoles:")
print(temperaturas_pereira['Miercoles'])

#Temperaturas de lunes a miercoles (por posicion)
print("\nTemperaturas de lunes a miercoles:")
print(temperaturas_pereira[0:3])


#Modificar la temperatura del viernes
temperaturas_pereira['Viernes'] = 28

print("\nTemperaturas después de modificar el viernes:")
print(temperaturas_pereira)


#Promedio de la semana
promedio = round(temperaturas_pereira.mean(), 2)

print("\nTemperatura promedio de la semana:")
print(promedio)


#Días con temperatura mayor a 22°C
dias_calurosos = temperaturas_pereira[temperaturas_pereira > 22]

print("\nDías con temperatura mayor a 22°C:")
print(dias_calurosos)


#Eliminar el sabado
temperaturas_pereira = temperaturas_pereira.drop('Sabado')

print("\nTemperaturas después de eliminar el sabado:")
print(temperaturas_pereira)


#Segunda ciudad y suma de series
temperaturas_medellin = pd.Series(
    [20, 22, 18, 21, 23, 24, 19],
    index=['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
)

print("\nTemperaturas de Medellin:")
print(temperaturas_medellin)

suma = temperaturas_pereira + temperaturas_medellin

print("\nSuma de temperaturas (Pereira + Medellin):")
print(suma)