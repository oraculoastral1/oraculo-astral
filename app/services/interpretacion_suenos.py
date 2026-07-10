"""
Motor de interpretación de sueños — Fase 4.

Recibe la descripción libre de un sueño, detecta símbolos conocidos,
y le pide a la IA (Groq, gratis) que interprete el sueño completo
combinando la mirada junguiana, la freudiana y el simbolismo detectado
— sin quedarse en un simple listado de significados.
"""
import os
import requests

from app.services.simbolos_suenos import detectar_simbolos

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "llama-3.3-70b-versatile"


def _construir_prompt(descripcion_sueño: str, simbolos: list[dict]) -> str:
    if simbolos:
        simbolos_texto = "\n".join(
            f"- {s['simbolo'].capitalize()}: mirada junguiana = {s['jung']}; mirada freudiana = {s['freud']}"
            for s in simbolos
        )
    else:
        simbolos_texto = "(no se detectaron símbolos del diccionario base; interpreta el sueño completo por su propia narrativa y emoción)"

    return f"""Eres un intérprete de sueños cálido y perspicaz, que combina la psicología
junguiana (arquetipos, inconsciente colectivo, individuación) y la freudiana
(deseos reprimidos, pulsiones, simbolismo) con el simbolismo onírico tradicional.
Escribes para una app en español dirigida a Latinoamérica. Tu tono es reflexivo,
cercano, nunca alarmista ni fatalista.

El sueño que la persona describió:
"{descripcion_sueño}"

Símbolos reconocidos en el diccionario de referencia:
{simbolos_texto}

Escribe una interpretación de 3 a 4 párrafos cortos que:
1. Interprete el sueño como una narrativa completa, no como una lista de símbolos sueltos
2. Ofrezca tanto la lectura junguiana (qué parte de la psique o arquetipo está en juego)
como un matiz freudiano donde sea relevante (sin forzarlo si el sueño no lo pide)
3. Termine con una pregunta reflexiva o sugerencia práctica para que la persona conecte
el sueño con su vida despierta

No uses encabezados ni listas. Escribe en prosa fluida, como si le hablaras directamente
a la persona. No afirmes certezas absolutas — los sueños se interpretan, no se decodifican
como un manual."""


def interpretar_sueño(descripcion_sueño: str) -> dict:
    """
    Genera la interpretación completa de un sueño.
    Requiere la variable de entorno GROQ_API_KEY (gratis en console.groq.com).
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Falta configurar GROQ_API_KEY en las variables de entorno del servidor."
        )

    simbolos = detectar_simbolos(descripcion_sueño)
    prompt = _construir_prompt(descripcion_sueño, simbolos)

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
    texto_interpretacion = respuesta.json()["choices"][0]["message"]["content"]

    return {
        "simbolos_detectados": simbolos,
        "interpretacion": texto_interpretacion,
    }
