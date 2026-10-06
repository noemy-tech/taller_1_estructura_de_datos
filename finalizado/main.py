# main.py
# ============================================================
# VISTA (la "V" de MVC). Solo habla con el usuario: pregunta con
# input(), muestra con print(). No valida reglas de negocio, no
# abre archivos: todo eso se lo pide al Controlador (views.py).
# ============================================================
from shared.herramientas import (
    imprimir_color,
    imprimir_titulo,
    imprimir_exito,
    imprimir_error,
    confirmar,
    limpiar_pantalla,
)
import views


def pedir_datos_estudiante():
    """Pide los 4 campos por consola y los junta en un diccionario."""
    print("Deja vacío un campo si no lo quieres cambiar (solo aplica al editar).\n")
    return {
        "nombre": input("Nombre: "),
        "edad": input("Edad: "),
        "carrera": input("Carrera: "),
        "correo": input("Correo: "),
    }


def mostrar_estudiante(estudiante):
    print(f" {estudiante}")


def texto_notas(cantidad):
    """1 -> '1 nota', 3 -> '3 notas'"""
    return f"{cantidad} nota" if cantidad == 1 else f"{cantidad} notas"


def opcion_crear():
    imprimir_titulo("Crear estudiante")
    datos = pedir_datos_estudiante()
    exito, mensaje = views.crear_estudiante(datos)
    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)


def opcion_listar():
    imprimir_titulo("Listado de estudiantes")
    estudiantes = views.obtener_todos()
    if not estudiantes:
        print("No hay estudiantes registrados todavía.")
    for estudiante in estudiantes:
        mostrar_estudiante(estudiante)


def opcion_buscar():
    imprimir_titulo("Buscar estudiante")
    termino = input("Escribe nombre, carrera o correo a buscar: ")
    resultados = views.buscar_estudiantes(termino)
    if not resultados:
        print("No se encontró nada con ese término.")
    for estudiante in resultados:
        mostrar_estudiante(estudiante)


def opcion_actualizar():
    imprimir_titulo("Actualizar estudiante")
    try:
        id_estudiante = int(input("Id del estudiante a editar: "))
    except ValueError:
        imprimir_error("El id debe ser un número")
        return

    estudiante = views.obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return

    mostrar_estudiante(estudiante)
    datos = pedir_datos_estudiante()
    exito, mensaje = views.actualizar_estudiante(id_estudiante, datos)
    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)


def opcion_eliminar():
    imprimir_titulo("Eliminar estudiante")
    try:
        id_estudiante = int(input("Id del estudiante a eliminar: "))
    except ValueError:
        imprimir_error("El id debe ser un número")
        return

    estudiante = views.obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return

    mostrar_estudiante(estudiante)
    if confirmar("¿Seguro que quieres eliminarlo?"):
        exito, mensaje = views.eliminar_estudiante(id_estudiante)
        imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
    else:
        print("Eliminación cancelada.")


def opcion_promedio():
    imprimir_titulo("Ver promedio")
    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número")
        return

    resultado = views.obtener_promedio(id_estudiante)
    if resultado is None:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return

    print(f"\nEstudiante: {resultado['nombre']}")
    if resultado["general"] is None:
        print("Todavía no tiene notas registradas.")
        return

    total = resultado["total_notas"]
    print(f"Notas obtenidas: {total}\n")

    # Cada materia con sus notas y el promedio que resulta de ellas
    for fila in resultado["detalle"]:
        notas_txt = ", ".join(f"{nota:g}" for nota in fila["notas"])
        print(f"  {fila['materia']} ({texto_notas(len(fila['notas']))}): {notas_txt}")
        print(f"      promedio de la materia: {fila['promedio']:.2f}")

    # El cálculo del promedio general, paso a paso
    suma_txt = " + ".join(f"{nota:g}" for nota in resultado["todas"])
    print("\nCálculo del promedio general:")
    print(f"  ({suma_txt}) / {total} = {resultado['general']:.2f}\n")
    imprimir_exito(
        f"Promedio general: {resultado['general']:.2f}  ({texto_notas(total)})"
    )


def opcion_agregar_nota():
    imprimir_titulo("Agregar nota")
    try:
        id_estudiante = int(input("Id del estudiante: "))
    except ValueError:
        imprimir_error("El id debe ser un número")
        return

    estudiante = views.obtener_por_id(id_estudiante)
    if not estudiante:
        imprimir_error(f"No existe un estudiante con id {id_estudiante}")
        return

    mostrar_estudiante(estudiante)
    print()
    materia = input("Materia: ")
    nota = input("Nota (0 a 10): ")
    exito, mensaje = views.agregar_nota(id_estudiante, materia, nota)
    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)


def mostrar_analisis_automatico(analisis):
    """Muestra el análisis de materias de TODOS los estudiantes registrados."""
    total = analisis["total_estudiantes"]
    imprimir_color(f"ANÁLISIS AUTOMÁTICO ({total} estudiantes registrados)\n", "AMARILLO")

    imprimir_color("Materias compartidas (2 o más estudiantes):", "AZUL")
    if not analisis["compartidas"]:
        print("  Ninguna materia la comparten 2 o más estudiantes.")
    for entrada in analisis["compartidas"]:
        quienes = ", ".join(f"{e['nombre']} (id {e['id']})" for e in entrada["estudiantes"])
        print(f"  • {entrada['materia']} [{len(entrada['estudiantes'])} de {total}] → {quienes}")

    print()
    imprimir_color("Materias comunes a TODOS los estudiantes:", "AZUL")
    if analisis["comunes_a_todos"]:
        for materia in analisis["comunes_a_todos"]:
            print(f"  • {materia}")
    else:
        print("  Ninguna.")

    print()
    imprimir_color("Materias que solo cursa un estudiante:", "AZUL")
    if not analisis["individuales"]:
        print("  Ninguna.")
    for entrada in analisis["individuales"]:
        e = entrada["estudiantes"][0]
        print(f"  • {entrada['materia']} → {e['nombre']} (id {e['id']})")


def comparar_estudiantes():
    """Apartado para comparar estudiantes concretos por su id."""
    print()
    texto = input("Ids a comparar separados por coma (ej: 1,2 o 1,2,3): ")
    try:
        ids = [int(parte) for parte in texto.split(",") if parte.strip()]
    except ValueError:
        imprimir_error("Los ids deben ser números separados por coma")
        return

    exito, mensaje, detalle = views.materias_en_comun(ids)
    if not exito:
        imprimir_error(mensaje)
        return

    print(f"\n{mensaje}")
    for fila in detalle:
        print(f"\n  {fila['materia']}")
        for e in fila["estudiantes"]:
            print(f"      {e['nombre']}: promedio {e['promedio']:.2f} ({texto_notas(e['cantidad'])})")


def opcion_materias_comunes():
    imprimir_titulo("Materias en común")
    analisis = views.analizar_materias()

    if analisis["total_estudiantes"] < 2:
        print("Necesitas al menos 2 estudiantes registrados para comparar materias.")
        input("\nPresiona Enter para continuar...")
        return
    if not analisis["compartidas"] and not analisis["individuales"]:
        print("Todavía no hay notas registradas, así que no hay materias para analizar.")
        input("\nPresiona Enter para continuar...")
        return

    mostrar_analisis_automatico(analisis)

    # Apartado interno: comparar estudiantes específicos
    while True:
        print()
        imprimir_color("-" * 55, "AZUL")
        print("1. Comparar estudiantes por id")
        print("2. Volver al menú principal")
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            comparar_estudiantes()
        elif opcion == "2":
            return
        else:
            imprimir_error("Opción no válida")


def menu_principal():
    while True:
        imprimir_titulo("CRUD de Estudiantes")
        print("1. Crear estudiante")
        print("2. Listar todos")
        print("3. Buscar")
        print("4. Actualizar")
        print("5. Eliminar")
        print("6. Limpiar consola")
        print("7. Ver promedio")
        print("8. Agregar nota")
        print("9. Materias en común")
        print("10. Salir")
        print()
        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            opcion_crear()
        elif opcion == "2":
            opcion_listar()
        elif opcion == "3":
            opcion_buscar()
        elif opcion == "4":
            opcion_actualizar()
        elif opcion == "5":
            opcion_eliminar()
        elif opcion == "6":
            limpiar_pantalla()
            continue  # vuelve directo al menú, sin pedir Enter de más
        elif opcion == "7":
            opcion_promedio()
        elif opcion == "8":
            opcion_agregar_nota()
        elif opcion == "9":
            opcion_materias_comunes()
            continue  # el apartado ya tiene su propia opción "Volver"
        elif opcion == "10":
            print("¡Hasta luego!")
            break
        else:
            imprimir_error("Opción no válida")

        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    menu_principal()
