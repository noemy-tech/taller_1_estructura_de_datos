# shared/herramientas.py
# ============================================================
# Funciones de apoyo reutilizables: no saben qué es un Estudiante,
# solo saben imprimir bonito y validar textos/números sueltos.
# ============================================================
import os

# DICCIONARIO: cada color tiene su etiqueta y su código de consola
COLORES = {
    "ROJO": "\033[91m",
    "VERDE": "\033[92m",
    "AZUL": "\033[94m",
    "AMARILLO": "\033[93m",
    "RESET": "\033[0m",
}

# TUPLAS: palabras aceptadas como "sí" o como "no". Son fijas, por eso
# son tuplas y no listas. Ya están sin tildes porque antes de comparar
# le quitamos las tildes a lo que escribe el usuario (ver quitar_tildes).
PALABRAS_SI = (
    "si", "s", "yes", "y", "positivo", "afirmativo", "afirmativa",
    "afirmo", "claro", "obvio", "correcto", "ok", "okey", "vale",
    "dale", "aja", "asi es", "por supuesto", "efectivamente", "exacto",
)

PALABRAS_NO = (
    "no", "n", "nel", "nunca", "jamas", "negativo", "negativa",
    "incorrecto", "falso", "nope", "para nada", "en absoluto",
)


def quitar_tildes(texto):
    """Cambia á,é,í,ó,ú por a,e,i,o,u para que 'sí' y 'si' se traten igual."""
    con_tilde = "áéíóú"
    sin_tilde = "aeiou"
    for i in range(len(con_tilde)):
        texto = texto.replace(con_tilde[i], sin_tilde[i])
    return texto


def limpiar_pantalla():
    os.system("clear" if os.name == "posix" else "cls")


def imprimir_color(texto, color):
    codigo = COLORES.get(color, COLORES["RESET"])
    print(f"{codigo}{texto}{COLORES['RESET']}")


def imprimir_titulo(texto):
    limpiar_pantalla()
    imprimir_color("=" * 55, "AZUL")
    print(f"  {texto}".center(55))
    imprimir_color("=" * 55, "AZUL")
    print()


def imprimir_exito(mensaje):
    imprimir_color(f"✓ {mensaje}", "VERDE")


def imprimir_error(mensaje):
    imprimir_color(f"✗ {mensaje}", "ROJO")


def confirmar(pregunta):
    """Pregunta sí/no admitiendo muchas variantes (positivo, afirmativo,
    negativo, nel, etc.). Si no reconoce la respuesta, vuelve a preguntar."""
    while True:
        respuesta = quitar_tildes(input(f"{pregunta} (si/no): ").strip().lower())

        if respuesta in PALABRAS_SI:
            return True
        if respuesta in PALABRAS_NO:
            return False

        imprimir_error("No entendí tu respuesta. Escribe algo como 'si' o 'no'.")


def es_numero_positivo(texto):
    """Valida que el texto sea un número entero mayor a 0. Sirve para la edad."""
    try:
        return int(texto) > 0
    except ValueError:
        return False


def es_email_valido(texto):
    """Validación mínima: un @, algo antes, algo después y un punto al final."""
    texto = texto.strip()
    if texto.count("@") != 1:
        return False
    usuario, dominio = texto.split("@")
    return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")


def es_nota_valida(texto, maximo=10):
    """Valida que el texto sea un número entre 0 y 'maximo'.
    Acepta coma o punto decimal (8,5 u 8.5)."""
    try:
        valor = float(str(texto).strip().replace(",", "."))
    except ValueError:
        return False
    return 0 <= valor <= maximo


def a_numero(texto):
    """Convierte '8,5' o '8.5' a float. Úsala después de es_nota_valida."""
    return float(str(texto).strip().replace(",", "."))
