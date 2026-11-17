import pandas as pd

#Crear la serie del inventario
inventario = pd.Series(
    [50, 30, 25, 15, 40, 8, 20],
    index=['Manzanas', 'Platanos', 'Naranjas', 'Peras', 'Uvas', 'Sandias', 'Cerezas']
)

print("Inventario inicial:")
print(inventario)


#Consultar cuantas naranjas hay
print("\nCantidad de naranjas:")
print(inventario['Naranjas'])


#Consultar total de productos en el inventario
print("\nTotal de productos en el inventario:")
print(inventario.sum())


#Actualizar el inventario
inventario['Platanos'] = inventario['Platanos'] - 5  
inventario['Manzanas'] = inventario['Manzanas'] + 20  

print("\nInventario despues de las ventas y compras:")
print(inventario)


#Identificar productos con poco stock (< 10)
poco_stock = inventario[inventario < 10]

print("\nProductos con menos de 10 unidades:")
print(poco_stock)


#Agregar un nuevo producto (Kiwis con 18 unidades)
inventario['Kiwis'] = 18

print("\nInventario despues de agregar kiwis:")
print(inventario)


#Eliminar las peras (agotadas)
inventario = inventario.drop('Peras')

print("\nInventario final (sin peras):")
print(inventario)