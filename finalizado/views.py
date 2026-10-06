# views.py
# ============================================================
# CONTROLADOR (aunque el archivo se llame "views.py", aquí no
# hay ni un print() ni un input(). Solo reglas: validar, buscar,
# decidir y guardar. La Vista (main.py) es la que habla con el
# usuario; este archivo solo le entrega resultados.
#
# Regla que se repite en las 5 funciones principales: siempre
# devuelven una TUPLA (exito, mensaje) o los datos pedidos.
# ============================================================
from models import Estudiante, CAMPOS_ESTUDIANTE, NOTA_MAXIMA, estudiante_desde_diccionario
from shared.json_manager import GestorJSON
from shared.herramientas import (
    es_numero_positivo,
    es_email_valido,
    es_nota_valida,
    a_numero,
    quitar_tildes,
)

gestor = GestorJSON("data/estudiantes.json")

# TUPLAS de configuración: fijas, nadie las cambia mientras corre el programa
CAMPOS_OBLIGATORIOS = ("nombre", "edad", "carrera", "correo")
CAMPOS_BUSCABLES = ("nombre", "carrera", "correo")


# ===================== AYUDAS INTERNAS =====================

def correos_registrados(excepto_id=None):
    """CONJUNTO con los correos ya usados (en minúscula), para revisar
    duplicados de forma instantánea, sin recorrer la lista dos veces."""
    return {
        registro["correo"].lower()
        for registro in gestor.leer()
        if registro["id"] != excepto_id
    }


def siguiente_id():
    ids = [registro["id"] for registro in gestor.leer()]
    return max(ids) + 1 if ids else 1


# ===================== C · CREATE =====================

def crear_estudiante(datos):
    """datos: diccionario con las claves de CAMPOS_ESTUDIANTE."""
    try:
        nombre = str(datos.get("nombre", "")).strip()
        edad_txt = str(datos.get("edad", "")).strip()
        carrera = str(datos.get("carrera", "")).strip()
        correo = str(datos.get("correo", "")).strip()

        # 1) Campos obligatorios
        if not nombre or not carrera or not correo:
            return False, "Nombre, carrera y correo son obligatorios"

        # 2) La edad debe ser un número entero positivo
        if not es_numero_positivo(edad_txt):
            return False, "La edad debe ser un número mayor a 0"

        # 3) Formato del correo
        if not es_email_valido(correo):
            return False, f"El correo '{correo}' no tiene un formato válido"

        # 4) Correo duplicado: búsqueda instantánea en el conjunto
        if correo.lower() in correos_registrados():
            return False, "Ese correo ya está registrado"

        # 5) Creo el objeto del Modelo
        estudiante = Estudiante(siguiente_id(), nombre, int(edad_txt), carrera, correo)

        # 6) Agrego a la lista de registros y guardo
        registros = gestor.leer()
        registros.append(estudiante.a_diccionario())
        if not gestor.guardar(registros):
            return False, "No se pudo escribir el archivo"

        return True, f"Estudiante '{estudiante.nombre}' creado con id {estudiante.id}"

    except Exception as error:
        return False, f"Error inesperado: {error}"


# ===================== R · READ =====================

def obtener_todos():
    """Devuelve una LISTA de objetos Estudiante."""
    return [estudiante_desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(id_estudiante):
    for estudiante in obtener_todos():
        if estudiante.id == id_estudiante:
            return estudiante
    return None


# ===================== S · SEARCH =====================

def buscar_estudiantes(termino):
    """Búsqueda lineal: revisa nombre, carrera y correo de cada registro."""
    termino = termino.strip().lower()
    if not termino:
        return []

    encontrados = []
    for registro in gestor.leer():
        for campo in CAMPOS_BUSCABLES:
            if termino in str(registro.get(campo, "")).lower():
                encontrados.append(estudiante_desde_diccionario(registro))
                break  # ya coincidió: paso al siguiente estudiante

    return encontrados


# ===================== U · UPDATE =====================

def actualizar_estudiante(id_estudiante, datos_nuevos):
    """datos_nuevos: diccionario con los campos que se quieren cambiar."""
    registros = gestor.leer()

    for posicion, registro in enumerate(registros):
        if registro["id"] == id_estudiante:

            correo_nuevo = str(datos_nuevos.get("correo", registro["correo"])).strip()
            if correo_nuevo and correo_nuevo.lower() in correos_registrados(excepto_id=id_estudiante):
                return False, f"Ese correo ya está registrado por otro estudiante"

            for campo in CAMPOS_ESTUDIANTE:
                if campo in datos_nuevos and str(datos_nuevos[campo]).strip() != "":
                    if campo == "edad":
                        if not es_numero_positivo(datos_nuevos[campo]):
                            return False, "La edad debe ser un número mayor a 0"
                        registro[campo] = int(datos_nuevos[campo])
                    elif campo == "correo":
                        if not es_email_valido(datos_nuevos[campo]):
                            return False, "El correo no tiene un formato válido"
                        registro[campo] = str(datos_nuevos[campo]).strip()
                    else:
                        registro[campo] = str(datos_nuevos[campo]).strip()

            registros[posicion] = registro
            if not gestor.guardar(registros):
                return False, "No se pudo escribir el archivo"
            return True, f"Estudiante con id {id_estudiante} actualizado"

    return False, f"No existe un estudiante con id {id_estudiante}"


# ===================== D · DELETE =====================

def eliminar_estudiante(id_estudiante):
    registros = gestor.leer()
    nuevos_registros = [r for r in registros if r["id"] != id_estudiante]

    if len(nuevos_registros) == len(registros):
        return False, f"No existe un estudiante con id {id_estudiante}"

    if not gestor.guardar(nuevos_registros):
        return False, "No se pudo escribir el archivo"

    return True, f"Estudiante con id {id_estudiante} eliminado"


# ===================== NOTAS Y PROMEDIO =====================

def _clave_materia(materia):
    """Clave para comparar materias sin importar mayúsculas ni tildes:
    'Matemáticas' y 'matematicas' cuentan como la misma materia."""
    return quitar_tildes(materia.strip().lower())


def agregar_nota(id_estudiante, materia, nota_txt):
    """Agrega una nota a un estudiante. Devuelve (exito, mensaje)."""
    materia = str(materia).strip()
    nota_txt = str(nota_txt).strip()

    if not materia:
        return False, "La materia es obligatoria"

    if not es_nota_valida(nota_txt, NOTA_MAXIMA):
        return False, f"La nota debe ser un número entre 0 y {NOTA_MAXIMA}"

    registros = gestor.leer()
    for registro in registros:
        if registro["id"] == id_estudiante:
            notas = registro.setdefault("notas", [])

            # Si el estudiante ya tiene esa materia, reutilizo su nombre
            # tal como la escribió la primera vez (evita duplicados raros)
            for n in notas:
                if _clave_materia(n["materia"]) == _clave_materia(materia):
                    materia = n["materia"]
                    break

            valor = a_numero(nota_txt)
            notas.append({"materia": materia, "nota": valor})

            if not gestor.guardar(registros):
                return False, "No se pudo escribir el archivo"
            return True, f"Nota {valor:g} agregada en '{materia}' a {registro['nombre']}"

    return False, f"No existe un estudiante con id {id_estudiante}"


def obtener_promedio(id_estudiante):
    """Devuelve un diccionario con todo el detalle de notas, o None si el id no existe.
      nombre       -> nombre del estudiante
      total_notas  -> cuántas notas ha obtenido
      todas        -> LISTA con cada nota, en el orden en que se ingresaron
      detalle      -> LISTA por materia: {"materia", "notas", "promedio"}
      general      -> promedio de todas las notas (None si no tiene notas)"""
    estudiante = obtener_por_id(id_estudiante)
    if estudiante is None:
        return None

    detalle = []
    for materia, lista in estudiante.notas_por_materia().items():
        detalle.append({
            "materia": materia,
            "notas": lista,
            "promedio": sum(lista) / len(lista),
        })

    return {
        "nombre": estudiante.nombre,
        "total_notas": len(estudiante.notas),
        "todas": [n["nota"] for n in estudiante.notas],
        "detalle": detalle,
        "general": estudiante.promedio_general(),
    }


# ===================== MATERIAS EN COMÚN =====================

def analizar_materias():
    """Análisis AUTOMÁTICO con todos los estudiantes registrados.
    Devuelve un diccionario:
      total_estudiantes -> cuántos estudiantes hay
      compartidas       -> materias que cursan 2 o más (con sus estudiantes)
      individuales      -> materias que solo cursa 1 estudiante
      comunes_a_todos   -> materias que cursan TODOS los estudiantes"""
    registros = gestor.leer()
    total = len(registros)
    por_materia = {}    # clave -> {"materia": nombre, "estudiantes": [{id, nombre}]}

    for registro in registros:
        vistas = set()  # para no contar dos veces la misma materia del mismo estudiante
        for n in registro.get("notas", []):
            clave = _clave_materia(n["materia"])
            if clave in vistas:
                continue
            vistas.add(clave)
            entrada = por_materia.setdefault(
                clave, {"materia": n["materia"], "estudiantes": []}
            )
            entrada["estudiantes"].append(
                {"id": registro["id"], "nombre": registro["nombre"]}
            )

    # Más estudiantes primero; a igualdad, orden alfabético
    def orden(entrada):
        return (-len(entrada["estudiantes"]), entrada["materia"].lower())

    compartidas = sorted(
        [e for e in por_materia.values() if len(e["estudiantes"]) >= 2], key=orden
    )
    individuales = sorted(
        [e for e in por_materia.values() if len(e["estudiantes"]) == 1], key=orden
    )
    comunes_a_todos = [
        e["materia"] for e in compartidas if total >= 2 and len(e["estudiantes"]) == total
    ]

    return {
        "total_estudiantes": total,
        "compartidas": compartidas,
        "individuales": individuales,
        "comunes_a_todos": comunes_a_todos,
    }


def materias_en_comun(ids):
    """COMPARAR estudiantes concretos: materias que comparten TODOS los ids indicados.
    Devuelve (exito, mensaje, detalle). 'detalle' es una LISTA por materia:
      {"materia": ..., "estudiantes": [{"nombre", "promedio", "cantidad"}]}
    con el promedio de cada estudiante en esa materia."""
    ids = list(dict.fromkeys(ids))      # quita ids repetidos conservando el orden
    if len(ids) < 2:
        return False, "Indica al menos 2 estudiantes distintos", []

    registros = {registro["id"]: registro for registro in gestor.leer()}
    estudiantes = []
    for id_estudiante in ids:
        registro = registros.get(id_estudiante)
        if registro is None:
            return False, f"No existe un estudiante con id {id_estudiante}", []
        estudiantes.append(estudiante_desde_diccionario(registro))

    # Por estudiante: {clave_materia: (nombre_materia, [notas])}
    por_estudiante = []
    for estudiante in estudiantes:
        agrupadas = {}
        for materia, lista in estudiante.notas_por_materia().items():
            agrupadas[_clave_materia(materia)] = (materia, lista)
        por_estudiante.append(agrupadas)

    claves_comunes = set.intersection(*[set(d) for d in por_estudiante])
    nombres = ", ".join(e.nombre for e in estudiantes)

    if not claves_comunes:
        return True, f"{nombres} no tienen materias en común", []

    detalle = []
    for clave in sorted(claves_comunes, key=lambda c: por_estudiante[0][c][0].lower()):
        fila = {"materia": por_estudiante[0][clave][0], "estudiantes": []}
        for estudiante, agrupadas in zip(estudiantes, por_estudiante):
            _, lista = agrupadas[clave]
            fila["estudiantes"].append({
                "nombre": estudiante.nombre,
                "promedio": sum(lista) / len(lista),
                "cantidad": len(lista),
            })
        detalle.append(fila)

    return True, f"Materias en común entre {nombres}:", detalle
