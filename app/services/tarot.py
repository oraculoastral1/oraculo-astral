"""
Tarot simplificado: los 22 arcanos mayores, con su significado
al derecho y al revés. Tirada aleatoria de una carta por lectura.
"""
import random

ARCANOS_MAYORES = [
    {"nombre": "El Loco", "derecho": "nuevos comienzos, espontaneidad, fe en el camino", "revertido": "imprudencia, dudas, riesgos mal calculados"},
    {"nombre": "El Mago", "derecho": "voluntad, habilidad para manifestar, recursos disponibles", "revertido": "manipulación, potencial desperdiciado"},
    {"nombre": "La Sacerdotisa", "derecho": "intuición, misterio, sabiduría interior", "revertido": "secretos ocultos, desconexión de la intuición"},
    {"nombre": "La Emperatriz", "derecho": "abundancia, creatividad, conexión con la naturaleza", "revertido": "bloqueo creativo, dependencia excesiva"},
    {"nombre": "El Emperador", "derecho": "estructura, autoridad, estabilidad", "revertido": "rigidez, control excesivo"},
    {"nombre": "El Sumo Sacerdote", "derecho": "tradición, guía espiritual, aprendizaje", "revertido": "dogmatismo, rebeldía necesaria"},
    {"nombre": "Los Enamorados", "derecho": "unión, decisiones del corazón, alineación de valores", "revertido": "desequilibrio, decisiones no alineadas"},
    {"nombre": "El Carro", "derecho": "voluntad firme, victoria, avance decidido", "revertido": "falta de dirección, control perdido"},
    {"nombre": "La Fuerza", "derecho": "coraje interior, paciencia, compasión", "revertido": "duda de uno mismo, energía mal canalizada"},
    {"nombre": "El Ermitaño", "derecho": "introspección, búsqueda interior, soledad elegida", "revertido": "aislamiento excesivo, evasión"},
    {"nombre": "La Rueda de la Fortuna", "derecho": "ciclos, destino, cambios inevitables", "revertido": "resistencia al cambio, mala fortuna temporal"},
    {"nombre": "La Justicia", "derecho": "equilibrio, verdad, consecuencias justas", "revertido": "injusticia, falta de responsabilidad"},
    {"nombre": "El Colgado", "derecho": "pausa, nueva perspectiva, rendición consciente", "revertido": "estancamiento, resistencia a soltar"},
    {"nombre": "La Muerte", "derecho": "transformación, cierre de ciclos, renacimiento", "revertido": "miedo al cambio, transición estancada"},
    {"nombre": "La Templanza", "derecho": "equilibrio, paciencia, integración de opuestos", "revertido": "desequilibrio, exceso"},
    {"nombre": "El Diablo", "derecho": "ataduras, tentación, sombra propia", "revertido": "liberación, ruptura de patrones"},
    {"nombre": "La Torre", "derecho": "ruptura súbita, revelación, caída de estructuras falsas", "revertido": "cambio evitado que se vuelve inevitable"},
    {"nombre": "La Estrella", "derecho": "esperanza, inspiración, fe renovada", "revertido": "desesperanza temporal, desconexión"},
    {"nombre": "La Luna", "derecho": "intuición, lo oculto, sueños e ilusiones", "revertido": "confusión, miedos irracionales"},
    {"nombre": "El Sol", "derecho": "alegría, vitalidad, éxito claro", "revertido": "optimismo excesivo, éxito retrasado"},
    {"nombre": "El Juicio", "derecho": "llamado interior, renacimiento, evaluación honesta", "revertido": "autocrítica excesiva, negación"},
    {"nombre": "El Mundo", "derecho": "cierre exitoso, plenitud, ciclo completado", "revertido": "asuntos inconclusos, sensación de estancamiento"},
]


def sacar_carta() -> dict:
    """Saca una carta al azar, con orientación (derecha o revertida) también al azar."""
    carta = random.choice(ARCANOS_MAYORES)
    revertida = random.random() < 0.5

    return {
        "carta": carta["nombre"],
        "orientacion": "revertida" if revertida else "derecha",
        "significado": carta["revertido"] if revertida else carta["derecho"],
    }
