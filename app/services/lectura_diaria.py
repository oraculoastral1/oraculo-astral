"""
Motor de lectura diaria — Fase 3 (v2 con tránsitos reales).

Toma la carta natal ya calculada, la numerología, una carta de tarot, y los
tránsitos planetarios de HOY (dónde están los planetas ahora mismo, comparados
contra la carta de nacimiento), y le pide a un modelo de IA (Groq, gratis, sin
tarjeta) que las fusione en un solo mensaje diario cálido y personal, en español.

Los tránsitos son el ingrediente que antes faltaba: sin ellos, dos días
distintos para la misma persona solo se diferenciaban por la carta de tarot
al azar. Con ellos, la lectura cambia por motivos astronómicos reales — el
mismo principio que usan los astrólogos profesionales.
"""
import os
import requests

from app.services.numerologia import calcular_camino_de_vida
from app.services.tarot import sacar_carta
from app.services.transitos import calcular_transitos_del_dia

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "llama-3.3-70b-versatile"


def _construir_prompt(carta_natal: dict, numerologia: dict, tarot: dict, transitos: list[dict]) -> str:
    sol = carta_natal["planetas"]["Sol"]
    luna = carta_natal["planetas"]["Luna"]
    ascendente = carta_natal["ascendente"]

    aspectos_texto = "; ".join(
        f"{a['planetas'][0]}-{a['planetas'][1]} en {a['aspecto']} ({a['naturaleza']})"
        for a in carta_natal["aspectos"][:4]  # los 4 aspectos más relevantes, para no saturar el prompt
    ) or "sin aspectos exactos destacados hoy"

    if transitos:
        transitos_texto = "; ".join(
            f"{t['planeta_en_transito']} en tránsito forma {t['aspecto']} con su "
            f"{t['planeta_natal']} natal ({t['naturaleza']})"
            for t in transitos[:3]  # los 3 tránsitos más exactos, ya vienen ordenados por relevancia
        )
    else:
        transitos_texto = "sin tránsitos exactos de planetas lentos hoy — es un día de calma relativa en ese sentido"

    return f"""Eres un guía espiritual cálido, cercano y sabio que escribe lecturas diarias
personalizadas para una app en español dirigida a Latinoamérica. Tu tono es íntimo,
esperanzador y directo — nunca genérico, nunca de horóscopo de periódico.

Datos de la persona para esta lectura:
- Sol en {sol['signo']} (casa {sol['casa']}), Luna en {luna['signo']} (casa {luna['casa']}), Ascendente en {ascendente['signo']}
- Aspectos permanentes de su carta natal: {aspectos_texto}
- Tránsitos activos HOY (esto es lo que hace que este día sea distinto a otros): {transitos_texto}
- Número de camino de vida (numerología): {numerologia['numero']} — {numerologia['significado']}
- Carta de tarot del día: {tarot['carta']} ({tarot['orientacion']}) — {tarot['significado']}

Escribe una lectura diaria de 3 a 4 párrafos cortos que:
1. Dé peso central a los tránsitos de HOY — son lo que hace que esta lectura sea de este día específico, no una genérica de su carta natal
2. Conecte todos los elementos en una sola narrativa coherente (no los enumeres por separado)
3. Dé un mensaje concreto y accionable para el día de hoy
4. Cierre con una reflexión breve e inspiradora

No uses encabezados ni listas. Escribe en prosa fluida, como si le hablaras directamente a la persona."""


def generar_lectura_diaria(fecha_nacimiento: str, carta_natal: dict) -> dict:
    """
    Genera la lectura diaria completa: numerología + tarot + tránsitos + fusión con IA.
    Requiere la variable de entorno GROQ_API_KEY (gratis en console.groq.com).
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta configurar GROQ_API_KEY en las variables de entorno del servidor."
        )

    numerologia = calcular_camino_de_vida(fecha_nacimiento)
    tarot = sacar_carta()
    transitos = calcular_transitos_del_dia(carta_natal)
    prompt = _construir_prompt(carta_natal, numerologia, tarot, transitos)

    respuesta = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODELO,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 500,
        },
        timeout=30,
    )
    respuesta.raise_for_status()
    texto_lectura = respuesta.json()["choices"][0]["message"]["content"]

    return {
        "numerologia": numerologia,
        "tarot": tarot,
        "transitos": transitos,
        "lectura": texto_lectura,
    }
