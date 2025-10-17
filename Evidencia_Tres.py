#!/usr/bin/env python3
# encoding: utf-8
"""
Sistema de Reservaciones de Salas
Cumple requisitos:
- Claves automáticas para Usuarios, Salas y Reservaciones (folio)
- Reservación asociada a cliente y sala
- Comprobación de disponibilidad por sala/fecha/turno
- Reservas con al menos 2 días de anticipación
- Eliminación sólo con >=3 días y con confirmación
- Reportes por fecha (tabular) y exportación a Excel
- Detección de primera ejecución (archivo DB inexistente)
"""

import os
import sys
import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta
import openpyxl

DB_FILE = "34.db"
TURNOS = ("M", "V", "N")  # Mañana, Tarde, Noche


def Crear_tabla():
    """Crea las tablas necesarias con claves autoincrement y restricciones."""
    try:
        with sqlite3.connect(DB_FILE) as conn:
            mi_cursor = conn.cursor()
            # Usuarios
            mi_cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuarios (
                    clave INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL
                );""")
            # Salas
            mi_cursor.execute("""
                CREATE TABLE IF NOT EXISTS Salas (
                    clave INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    capacidad INTEGER NOT NULL CHECK (capacidad > 0)
                );""")
            # Reservaciones: asociadas a cliente y sala
            mi_cursor.execute("""
                CREATE TABLE IF NOT EXISTS Reservaciones (
                    folio INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_clave INTEGER NOT NULL,
                    sala_clave INTEGER NOT NULL,
                    nombre TEXT NOT NULL,
                    horario TEXT NOT NULL,
                    fecha TEXT NOT NULL,  -- guardamos YYYY-MM-DD
                    FOREIGN KEY(cliente_clave) REFERENCES Usuarios(clave),
                    FOREIGN KEY(sala_clave) REFERENCES Salas(clave)
                );""")
            conn.commit()
            print("Tablas creadas o ya existentes (OK).")
    except Error as e:
        print("Error al crear tablas:", e)
    except Exception as e:
        print("Se produjo el siguiente error:", e)


def es_fecha_valida_str(fecha_str):
    try:
        dt = datetime.strptime(fecha_str, "%d/%m/%Y")
        return dt
    except ValueError:
        return None


def Registrar_Cliente():
    while True:
        Usuario = input("Ingresa el nombre del cliente (Escribe SALIR para regresar): ").strip()
        if Usuario.upper() == 'SALIR':
            return
        if not Usuario:
            print("El nombre del usuario no puede estar vacío.")
            continue
        try:
            with sqlite3.connect(DB_FILE) as conn:
                mi_cursor = conn.cursor()
                mi_cursor.execute("INSERT INTO Usuarios (nombre) VALUES (?)", (Usuario,))
                conn.commit()
                clave = mi_cursor.lastrowid
                print("Usuario registrado!")
                print(f"Tu clave de usuario es: {clave}")
                return
        except Error as e:
            print("Error al registrar usuario:", e)
        except Exception as e:
            print("Surgió una falla siendo esta la causa:", e)


def Registrar_Sala():
    while True:
        SALA = input("¿Cómo se va a llamar la sala? (Escribe SALIR para regresar): ").strip()
        if SALA.upper() == 'SALIR':
            return
        if not SALA:
            print("El nombre de la sala no puede estar vacío.")
            continue
        try:
            capacity_str = input("¿Cuál va a ser la capacidad?: ").strip()
            capacity = int(capacity_str)
            if capacity <= 0:
                print("La capacidad debe ser mayor que cero.")
                continue
        except ValueError:
            print("Introduce un número válido para la capacidad.")
            continue

        try:
            with sqlite3.connect(DB_FILE) as conn:
                mi_cursor = conn.cursor()
                mi_cursor.execute("INSERT INTO Salas (nombre, capacidad) VALUES (?, ?)", (SALA, capacity))
                conn.commit()
                clave = mi_cursor.lastrowid
                print("Sala registrada!")
                print(f"Tu clave de la sala es: {clave}")
                return
        except Error as e:
            print("Error al registrar sala:", e)
        except Exception as e:
            print("Surgió una falla siendo esta la causa:", e)


def listar_salas():
    with sqlite3.connect(DB_FILE) as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("SELECT clave, nombre, capacidad FROM Salas ORDER BY clave")
        return mi_cursor.fetchall()


def existe_cliente(clave):
    with sqlite3.connect(DB_FILE) as conn:
        mi_cursor = conn.cursor()
        mi_cursor.execute("SELECT nombre FROM Usuarios WHERE clave = ?", (clave,))
        return mi_cursor.fetchone()


def Registrar_Reservacion():
    while True:
        try:
            valor_clave_str = input("¿Cuál es tu clave de cliente (Escribe SALIR para regresar)?: ").strip()
            if valor_clave_str.upper() == 'SALIR':
                return
            valor_clave = int(valor_clave_str)
        except ValueError:
            print("Clave inválida. Intenta de nuevo.")
            continue

        cliente = existe_cliente(valor_clave)
        if not cliente:
            print(f"No se encontró un cliente asociado con la clave {valor_clave}")
            continue
        print(f"Cliente: {cliente[0]} (clave {valor_clave})")

        salas = listar_salas()
        if not salas:
            print("No hay salas registradas. Registre primero una sala.")
            return
        print("Salas disponibles (clave, nombre, capacidad):")
        for c, n, cap in salas:
            print(f"{c}\t{n}\t(capacidad: {cap})")

        try:
            sala_clave_str = input("Introduce la clave de la sala que deseas: ").strip()
            sala_clave = int(sala_clave_str)
        except ValueError:
            print("Clave de sala inválida.")
            continue

        # validar que la sala exista
        sala_ex = None
        for c, n, cap in salas:
            if c == sala_clave:
                sala_ex = (c, n, cap)
                break
        if not sala_ex:
            print("Sala no encontrada.")
            continue

        Nombre = input("Ingresa el nombre de la reservación (Escribe SALIR para regresar): ").strip()
        if Nombre.upper() == 'SALIR':
            return
        if not Nombre:
            print("El nombre de la reservación no puede estar vacío.")
            continue

        Horario = input("¿Cuál es el horario que quieres? [M, V, N]: ").strip().upper()
        if Horario not in TURNOS:
            print("Horario inválido. Usa M, V o N.")
            continue

        Fecha_Ingresada = input("Ingresa la fecha de reservación (dd/mm/aaaa): ").strip()
        Fecha_dt = es_fecha_valida_str(Fecha_Ingresada)
        if not Fecha_dt:
            print("Formato de fecha no válido. Usa dd/mm/aaaa.")
            continue

        hoy = datetime.now().date()
        if Fecha_dt.date() < (hoy + timedelta(days=2)):
            print("Debes hacer la reservación con al menos 2 días de anticipación.")
            continue

        # Comprobar conflicto: misma sala, misma fecha, mismo horario
        try:
            with sqlite3.connect(DB_FILE) as conn:
                mi_cursor = conn.cursor()
                mi_cursor.execute(
                    "SELECT 1 FROM Reservaciones WHERE sala_clave = ? AND fecha = ? AND horario = ? LIMIT 1",
                    (sala_clave, Fecha_dt.date().isoformat(), Horario)
                )
                if mi_cursor.fetchone():
                    print("La sala ya está reservada para esa fecha y turno.")
                    continue

                # Insertar reservación
                mi_cursor.execute(
                    "INSERT INTO Reservaciones (cliente_clave, sala_clave, nombre, horario, fecha) VALUES (?, ?, ?, ?, ?)",
                    (valor_clave, sala_clave, Nombre, Horario, Fecha_dt.date().isoformat())
                )
                conn.commit()
                folio = mi_cursor.lastrowid
                print("¡Reservación Realizada con éxito!")
                print(f"Folio asignado: {folio}")
                return
        except Error as e:
            print("Error al insertar reservación:", e)
        except Exception as e:
            print("Surgió una falla siendo esta la causa:", e)


def modificar_descripciones():
    """
    Modifica la descripción (nombre del evento) de una reservación identificada por folio.
    """
    while True:
        folio_str = input("Introduce el folio de la reservación a modificar (o SALIR): ").strip()
        if folio_str.upper() == 'SALIR':
            return
        try:
            folio = int(folio_str)
        except ValueError:
            print("Folio inválido.")
            continue

        try:
            with sqlite3.connect(DB_FILE) as conn:
                mi_cursor = conn.cursor()
                mi_cursor.execute("""
                    SELECT r.folio, u.nombre, s.nombre, r.nombre, r.horario, r.fecha
                    FROM Reservaciones r
                    JOIN Usuarios u ON r.cliente_clave = u.clave
                    JOIN Salas s ON r.sala_clave = s.clave
                    WHERE r.folio = ?
                """, (folio,))
                registro = mi_cursor.fetchone()
                if not registro:
                    print(f"No se encontró una reservación con folio {folio}.")
                    continue

                print("Datos actuales de la reservación:")
                print("Folio\tCliente\tSala\tEvento\tHorario\tFecha")
                print(f"{registro[0]}\t{registro[1]}\t{registro[2]}\t{registro[3]}\t{registro[4]}\t{registro[5]}")
                nuevo_nombre = input("Introduce el nuevo nombre del evento (o ENTER para cancelar): ").strip()
                if not nuevo_nombre:
                    print("Operación cancelada.")
                    return

                mi_cursor.execute("UPDATE Reservaciones SET nombre = ? WHERE folio = ?", (nuevo_nombre, folio))
                conn.commit()
                print("Modificación realizada con éxito.")
                return
        except Error as e:
            print("Error al modificar:", e)
        except Exception as e:
            print("Surgió una falla siendo esta la causa:", e)


def consulta_fecha():
    fecha_consultar = input("Dime una fecha (dd/mm/aaaa): ").strip()
    Fecha_dt = es_fecha_valida_str(fecha_consultar)
    if not Fecha_dt:
        print("Formato de fecha no válido. Por favor, ingresa la fecha en el formato correcto (dd/mm/aaaa).")
        return

    fecha_iso = Fecha_dt.date().isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            mi_cursor = conn.cursor()
            # Obtener todas las salas
            mi_cursor.execute("SELECT clave, nombre FROM Salas ORDER BY clave")
            salas = mi_cursor.fetchall()
            if not salas:
                print("No hay salas registradas.")
                return

            disponibles = []
            for sala_clave, sala_nombre in salas:
                for t in TURNOS:
                    mi_cursor.execute(
                        "SELECT 1 FROM Reservaciones WHERE sala_clave = ? AND fecha = ? AND horario = ? LIMIT 1",
                        (sala_clave, fecha_iso, t)
                    )
                    if mi_cursor.fetchone() is None:
                        disponibles.append((sala_clave, sala_nombre, t))

            if disponibles:
                print(f"Opciones disponibles para la fecha {Fecha_dt.strftime('%d/%m/%Y')}:")
                print("Clave\tSala\tTurno")
                for c, n, t in disponibles:
                    print(f"{c}\t{n}\t{t}")
            else:
                print(f"No hay opciones disponibles para la fecha {Fecha_dt.strftime('%d/%m/%Y')}.")
    except Error as e:
        print("Error en la consulta:", e)
    except Exception as e:
        print("Se produjo el siguiente error:", e)


def reporte_reservaciones_por_fecha():
    fecha_consultar = input("Dime una fecha (dd/mm/aaaa): ").strip()
    Fecha_dt = es_fecha_valida_str(fecha_consultar)
    if not Fecha_dt:
        print("Formato de fecha no válido. Por favor, ingresa la fecha en el formato correcto (dd/mm/aaaa).")
        return

    fecha_iso = Fecha_dt.date().isoformat()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT r.folio, u.nombre AS cliente, s.clave AS sala_clave, s.nombre AS sala_nombre,
                       r.horario, r.fecha, r.nombre AS evento
                FROM Reservaciones r
                JOIN Usuarios u ON r.cliente_clave = u.clave
                JOIN Salas s ON r.sala_clave = s.clave
                WHERE r.fecha = ?
                ORDER BY s.clave, r.horario;
            """, (fecha_iso,))
            registros = mi_cursor.fetchall()

            if registros:
                print(f"Reservaciones para la fecha {Fecha_dt.strftime('%d/%m/%Y')}:")
                print("Folio\tCliente\tSalaClave\tSalaNombre\tHorario\tFecha\tEvento")
                for folio, cliente, sala_clave, sala_nombre, horario, fecha, evento in registros:
                    print(f"{folio}\t{cliente}\t{sala_clave}\t{sala_nombre}\t{horario}\t{fecha}\t{evento}")
                # Preguntar si desea exportar este reporte
                opcion = input("¿Quieres exportar este reporte a Excel? (S/N): ").strip().upper()
                if opcion == 'S':
                    exportar_registros_a_excel(registros, Fecha_dt.strftime("%Y-%m-%d"))
            else:
                print("No hay reservaciones para esa fecha.")
    except Error as e:
        print("Error al obtener reporte:", e)
    except Exception as e:
        print("Se produjo el siguiente error:", e)


def exportar_registros_a_excel(registros, etiqueta_fecha=""):
    """
    Exporta una lista de tuples a Excel.
    registros: iterable de (folio, cliente, sala_clave, sala_nombre, horario, fecha, evento)
    etiqueta_fecha: texto para el nombre del archivo
    """
    try:
        workbook = openpyxl.Workbook()
        hoja = workbook.active
        hoja.title = "Reservaciones"
        encabezados = ['Folio', 'Cliente', 'SalaClave', 'SalaNombre', 'Horario', 'Fecha', 'Evento']
        hoja.append(encabezados)
        for r in registros:
            hoja.append(r)
        filename = f"Reporte_Reservaciones_{etiqueta_fecha or 'todos'}.xlsx"
        workbook.save(filename)
        print(f"Reporte exportado exitosamente como '{filename}'")
    except Exception as e:
        print("Error al exportar a Excel:", e)


def exportar_base_de_datos_a_excel():
    """
    Exporta todas las reservaciones (unidas con cliente y sala) o las de una fecha específica si el usuario lo solicita.
    """
    opcion = input("¿Deseas exportar (1) Todas las reservaciones o (2) Reservaciones de una fecha? [1/2]: ").strip()
    if opcion == '2':
        fecha_consultar = input("Dime la fecha (dd/mm/aaaa): ").strip()
        Fecha_dt = es_fecha_valida_str(fecha_consultar)
        if not Fecha_dt:
            print("Formato de fecha inválido.")
            return
        fecha_iso = Fecha_dt.date().isoformat()
        with sqlite3.connect(DB_FILE) as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT r.folio, u.nombre AS cliente, s.clave AS sala_clave, s.nombre AS sala_nombre,
                       r.horario, r.fecha, r.nombre AS evento
                FROM Reservaciones r
                JOIN Usuarios u ON r.cliente_clave = u.clave
                JOIN Salas s ON r.sala_clave = s.clave
                WHERE r.fecha = ?
                ORDER BY s.clave, r.horario;
            """, (fecha_iso,))
            registros = mi_cursor.fetchall()
            if registros:
                exportar_registros_a_excel(registros, Fecha_dt.strftime("%Y-%m-%d"))
            else:
                print("No hay reservaciones para esa fecha.")
    else:
        try:
            with sqlite3.connect(DB_FILE) as conn:
                mi_cursor = conn.cursor()
                mi_cursor.execute("""
                    SELECT r.folio, u.nombre AS cliente, s.clave AS sala_clave, s.nombre AS sala_nombre,
                           r.horario, r.fecha, r.nombre AS evento
                    FROM Reservaciones r
                    JOIN Usuarios u ON r.cliente_clave = u.clave
                    JOIN Salas s ON r.sala_clave = s.clave
                    ORDER BY r.fecha, s.clave, r.horario;
                """)
                registros = mi_cursor.fetchall()
                if registros:
                    exportar_registros_a_excel(registros, "todas")
                else:
                    print("No hay reservaciones en la base de datos.")
        except Exception as e:
            print("Error al exportar:", e)


def eliminar_reservacion():
    folio_str = input("Introduce el folio de la reservación que deseas eliminar (o SALIR): ").strip()
    if folio_str.upper() == 'SALIR':
        return
    try:
        folio = int(folio_str)
    except ValueError:
        print("Folio inválido.")
        return

    try:
        with sqlite3.connect(DB_FILE) as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT r.folio, u.nombre AS cliente, s.nombre AS sala, r.nombre AS evento, r.horario, r.fecha
                FROM Reservaciones r
                JOIN Usuarios u ON r.cliente_clave = u.clave
                JOIN Salas s ON r.sala_clave = s.clave
                WHERE r.folio = ?
            """, (folio,))
            registro = mi_cursor.fetchone()
            if not registro:
                print(f"No se encontró una reservación con folio {folio}.")
                return

            print("Reservación encontrada:")
            print("Folio\tCliente\tSala\tEvento\tHorario\tFecha")
            print(f"{registro[0]}\t{registro[1]}\t{registro[2]}\t{registro[3]}\t{registro[4]}\t{registro[5]}")

            # verificar regla de 3 días
            fecha_res = datetime.fromisoformat(registro[5]).date()
            dias_restantes = (fecha_res - datetime.now().date()).days
            if dias_restantes < 3:
                print("Solo pueden eliminarse reservaciones con al menos 3 días de anticipación.")
                return

            confirm = input("¿Confirma eliminación? Esto NO se puede deshacer. (S/N): ").strip().upper()
            if confirm != 'S':
                print("Eliminación cancelada.")
                return

            mi_cursor.execute("DELETE FROM Reservaciones WHERE folio = ?", (folio,))
            conn.commit()
            if mi_cursor.rowcount > 0:
                print(f"Reservación con folio {folio} eliminada exitosamente.")
            else:
                print("No se pudo eliminar (posible condición de carrera).")
    except Exception as e:
        print("Se produjo el siguiente error:", e)


def menu():
    # Al iniciar el programa, detectar si es la primera ejecución.
    if not os.path.exists(DB_FILE):
        print("Parece ser la primera ejecución. Se creará la base de datos y sus estructuras.")
    Crear_tabla()

    while True:
        print("\n---- MENÚ ----")
        print("1. Registrar Reservación")
        print("2. Modificar las descripciones de la reservación (por folio)")
        print("3. Consultar disponibilidad por fecha")
        print("4. Reporte de las reservaciones de una fecha")
        print("5. Registrar Sala")
        print("6. Registrar Cliente")
        print("7. Salir del programa")
        print("8. Eliminar reservación")
        print("9. Exportar base de datos a Excel")
        try:
            opcion = int(input("Selecciona una opción (1-9): ").strip())
            if opcion == 1:
                Registrar_Reservacion()
            elif opcion == 2:
                modificar_descripciones()
            elif opcion == 3:
                consulta_fecha()
            elif opcion == 4:
                reporte_reservaciones_por_fecha()
            elif opcion == 5:
                Registrar_Sala()
            elif opcion == 6:
                Registrar_Cliente()
            elif opcion == 7:
                print("Saliendo del programa...")
                sys.exit(0)
            elif opcion == 8:
                eliminar_reservacion()
            elif opcion == 9:
                exportar_base_de_datos_a_excel()
            else:
                print("Opción no válida. Por favor, selecciona un número entre 1 y 9.")
        except ValueError:
            print("Entrada no válida. Por favor, ingresa un número entre 1 y 9.")
        except KeyboardInterrupt:
            print("\nInterrupción. Saliendo.")
            sys.exit(0)


if __name__ == "__main__":
    menu()
