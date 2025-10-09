# =========================
# Ejercicios con Conjuntos en Python
# =========================

# Ejercicio 1 – Unión de conjuntos
# Une ambos conjuntos usando .union() y muestra el resultado
A = {"manzana", "pera", "uva"}
B = {"uva", "sandía", "mango"}
print("Ejercicio 1:", A.union(B))


# Ejercicio 2 – Eliminar un elemento específico
# Usa .remove() para eliminar "pera" y luego intenta eliminar "fresa"
frutas = {"manzana", "pera", "sandía", "mango"}
frutas.remove("pera")
print("Ejercicio 2 (después de eliminar 'pera'):", frutas)
# frutas.remove("fresa")  # <- Descomenta y verás que da error


# Ejercicio 3 – Eliminar un elemento al azar
numeros = {10, 20, 30, 40, 50}
print("Ejercicio 3 (elemento eliminado con pop):", numeros.pop())
print("Conjunto ahora:", numeros)


# Ejercicio 4 – Diferencia entre conjuntos
A = {1, 2, 3, 4, 5}
B = {4, 5, 6, 7}
print("Ejercicio 4 (A - B):", A.difference(B))
print("Ejercicio 4 (B - A):", B.difference(A))


# Ejercicio 5 – Intersección entre conjuntos
estudiantes_python = {"Ana", "Luis", "Pedro", "Marta"}
estudiantes_java = {"Marta", "Sofía", "Pedro", "Carlos"}
print("Ejercicio 5 (intersección):", estudiantes_python.intersection(estudiantes_java))


# Ejercicio 6 – Intersección y actualización
A = {1, 2, 3, 4, 5}
B = {3, 4, 5, 6}
A.intersection_update(B)
print("Ejercicio 6 (A después de intersection_update):", A)


# Ejercicio 7 – Diferencia y actualización
colores_A = {"rojo", "azul", "verde", "amarillo"}
colores_B = {"verde", "amarillo", "negro"}
colores_A.difference_update(colores_B)
print("Ejercicio 7 (colores_A después de difference_update):", colores_A)


# Ejercicio 8 – Reto combinado
A = {1, 2, 3, 4, 5, 6}
B = {4, 5, 6, 7, 8, 9}
print("Ejercicio 8 (unión):", A.union(B))
print("Ejercicio 8 (intersección):", A.intersection(B))
print("Ejercicio 8 (A - B):", A.difference(B))
print("Ejercicio 8 (B - A):", B.difference(A))

