"""
Diccionario de símbolos oníricos frecuentes.
Cada símbolo trae dos lecturas: la junguiana (arquetipos, inconsciente
colectivo) y la freudiana (deseos reprimidos, pulsiones). Se usan como
base de referencia para que la IA interprete el sueño completo, no
como un "diccionario de significados" a buscar y pegar.
"""

SIMBOLOS = {
    "agua": {
        "jung": "el inconsciente mismo; aguas calmas hablan de paz interior, aguas turbulentas de emociones no procesadas",
        "freud": "deseo, a veces de connotación sexual o de nacimiento (el agua como líquido amniótico)",
    },
    "casa": {
        "jung": "la psique de quien sueña; cada habitación representa una parte distinta del ser",
        "freud": "el propio cuerpo, especialmente si hay puertas o pasillos ocultos",
    },
    "caida": {
        "jung": "pérdida de control o de una posición sostenida conscientemente",
        "freud": "ansiedad ante el fracaso o pérdida de estatus",
    },
    "volar": {
        "jung": "liberación, trascendencia del ego, deseo de perspectiva más amplia",
        "freud": "deseo de libertad, a veces vinculado a impulsos reprimidos",
    },
    "dientes": {
        "jung": "vitalidad y poder personal; perderlos habla de una crisis de autoimagen",
        "freud": "ansiedad de castración o miedo a envejecer/perder atractivo",
    },
    "muerte": {
        "jung": "fin de una etapa psicológica, transformación necesaria — casi nunca literal",
        "freud": "deseo reprimido de terminar con una situación o relación",
    },
    "persecucion": {
        "jung": "una sombra propia no reconocida que se intenta evitar",
        "freud": "culpa o un impulso propio que se rechaza conscientemente",
    },
    "desnudez": {
        "jung": "vulnerabilidad ante el mundo, mostrarse sin máscaras",
        "freud": "miedo a la exposición, vergüenza reprimida",
    },
    "examenes": {
        "jung": "autoevaluación del propio progreso o valor personal",
        "freud": "ansiedad de desempeño transferida de otra área de la vida",
    },
    "serpiente": {
        "jung": "transformación, sabiduría instintiva, energía vital (símbolo muy antiguo y ambivalente)",
        "freud": "simbolismo fálico, o de una tentación/peligro percibido",
    },
    "bebe": {
        "jung": "algo nuevo naciendo en la psique — un proyecto, una parte de sí mismo",
        "freud": "deseo de maternidad/paternidad, o de cuidar una parte vulnerable de sí",
    },
    "fuego": {
        "jung": "transformación intensa, pasión, purificación",
        "freud": "deseo o ira reprimida buscando expresión",
    },
    "espejo": {
        "jung": "confrontación con la propia sombra o con la verdadera identidad",
        "freud": "narcisismo o ansiedad sobre la propia imagen",
    },
}


def detectar_simbolos(descripcion_sueño: str) -> list[dict]:
    """
    Busca símbolos conocidos dentro de la descripción libre que da la persona.
    Búsqueda flexible (sin tildes, insensible a mayúsculas).
    """
    texto = (
        descripcion_sueño.lower()
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u")
    )

    encontrados = []
    for simbolo, significados in SIMBOLOS.items():
        if simbolo in texto:
            encontrados.append({"simbolo": simbolo, **significados})

    return encontrados
