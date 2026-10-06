# models.py
# ============================================================
# MODELO (la "M" de MVC)
# Aquí solo decimos QUÉ ES un estudiante. Nada de print(), nada
# de input(), nada de abrir archivos. Eso le toca a otras capas.
# ============================================================

# TUPLA: el orden y los nombres de los campos son fijos.
# La usamos en el Controlador y en la Vista para no repetir
# los mismos textos sueltos en varias partes del programa.
CAMPOS_ESTUDIANTE = ("nombre", "edad", "carrera", "correo")

# La nota va de 0 a 10 (escala usada en Ecuador)
NOTA_MAXIMA = 10


class Estudiante:
    """Representa a un estudiante."""

    def __init__(self, id_estudiante, nombre, edad, carrera, correo, notas=None):
        self.id = id_estudiante        # no usamos 'id' como nombre de parámetro
        self.nombre = nombre
        self.edad = edad                # número (int)
        self.carrera = carrera
        self.correo = correo
        # LISTA de diccionarios: [{"materia": "Matemáticas", "nota": 8.5}, ...]
        self.notas = notas if notas is not None else []

    def a_diccionario(self):
        """Objeto -> diccionario. Así se puede guardar en el JSON."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "edad": self.edad,
            "carrera": self.carrera,
            "correo": self.correo,
            "notas": self.notas,
        }

    def promedio_general(self):
        """Promedio de TODAS las notas. Devuelve None si no tiene notas."""
        if not self.notas:
            return None
        return sum(n["nota"] for n in self.notas) / len(self.notas)

    def notas_por_materia(self):
        """DICCIONARIO {materia: [notas]}. Una materia puede tener varias notas."""
        agrupado = {}
        for n in self.notas:
            agrupado.setdefault(n["materia"], []).append(n["nota"])
        return agrupado

    def promedio_por_materia(self):
        """DICCIONARIO {materia: promedio}."""
        return {
            materia: sum(lista) / len(lista)
            for materia, lista in self.notas_por_materia().items()
        }

    def __str__(self):
        return f"[{self.id}] {self.nombre} - {self.edad} años - {self.carrera} - {self.correo}"


def estudiante_desde_diccionario(datos):
    """Diccionario -> objeto Estudiante. Función normal, sin @classmethod.
    Si el registro es antiguo y no tiene 'notas', se usa una lista vacía."""
    return Estudiante(
        datos["id"],
        datos["nombre"],
        datos["edad"],
        datos["carrera"],
        datos["correo"],
        datos.get("notas", []),
    )
