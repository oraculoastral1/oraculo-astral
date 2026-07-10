"""
Numerología pitagórica simple: número de "camino de vida",
calculado a partir de la fecha de nacimiento completa.
"""

SIGNIFICADOS = {
    1: "liderazgo, independencia, iniciar cosas nuevas",
    2: "cooperación, sensibilidad, equilibrio en relaciones",
    3: "expresión creativa, comunicación, alegría",
    4: "estructura, disciplina, construir bases sólidas",
    5: "libertad, cambio, aventura",
    6: "responsabilidad, cuidado de otros, armonía en el hogar",
    7: "introspección, espiritualidad, búsqueda de verdad",
    8: "poder personal, logros materiales, ambición",
    9: "humanitarismo, cierre de ciclos, sabiduría",
    11: "número maestro — intuición elevada, inspiración espiritual",
    22: "número maestro — el 'constructor maestro', grandes visiones hechas realidad",
    33: "número maestro — maestría espiritual al servicio de otros",
}


def _reducir(numero: int) -> int:
    """Reduce un número a un solo dígito, preservando los números maestros 11, 22, 33."""
    while numero > 9 and numero not in (11, 22, 33):
        numero = sum(int(d) for d in str(numero))
    return numero


def calcular_camino_de_vida(fecha: str) -> dict:
    """
    fecha: 'YYYY-MM-DD'
    Suma todos los dígitos de la fecha de nacimiento y los reduce
    a un número de camino de vida (1-9, u 11/22/33 si son maestros).
    """
    digitos = [int(d) for d in fecha if d.isdigit()]
    suma_total = sum(digitos)
    numero = _reducir(suma_total)

    return {
        "numero": numero,
        "significado": SIGNIFICADOS[numero],
        "es_numero_maestro": numero in (11, 22, 33),
    }
