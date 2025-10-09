# Lista de compradores (LIST)
entradas = ["Ana", "Luis", "Ana", "Carlos", "Sofía", "Luis"]

# 1. Cantidad de entradas vendidas
print("Entradas vendidas:", len(entradas))

# 2. Lista completa en orden
print("Lista de compradores en orden de compra:")
for comprador in entradas:
    print("-", comprador)

# 3. Primer y último comprador
print("Primer comprador:", entradas[0])
print("Último comprador:", entradas[-1])




# Coordenadas (TUPLE)
coordenadas = (19.4326, -99.1332)  # Ciudad de México

# 1. Imprimir latitud y longitud
print("Latitud:", coordenadas[0])
print("Longitud:", coordenadas[1])

# 2. Verificar hemisferio
if coordenadas[0] > 0:
    print("Hemisferio Norte")
else:
    print("Hemisferio Sur")

if coordenadas[1] < 0:
    print("Hemisferio Occidental")
else:
    print("Hemisferio Oriental")





# Entregas de alumnos (SET)
entregas = {"Ana", "Luis", "Ana", "Sofía", "Carlos", "Luis"} 
 # Python elimina duplicados automáticamente

# 1. Alumnos únicos
print("Alumnos que entregaron:", entregas)

# 2. Verificar si Pedro entregó
if "Pedro" in entregas:
    print("Pedro entregó el trabajo.")
else:
    print("Pedro no entregó el trabajo.")

# 3. Contar alumnos distintos
print("Cantidad de alumnos distintos:", len(entregas))





# Productos y precios (DICT)
productos = {"manzana": 10, "pan": 15, "leche": 25}

# 1. Precio de la leche
print("Precio de la leche:", productos["leche"])

# 2. Agregar huevo
productos["huevo"] = 20

# 3. Cambiar precio del pan
productos["pan"] = 18

# 4. Mostrar todos los productos
print("Lista de productos y precios:")
for producto, precio in productos.items():
    print(f"- {producto}: {precio}")

