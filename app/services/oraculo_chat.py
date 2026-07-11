"""
Motor de "Pregúntale al oráculo" — Mejora #7.

A diferencia de la lectura diaria (fija, generada automáticamente), aquí
la persona hace una pregunta puntual y libre ("¿debería tomar este
trabajo?", "¿por qué me cuesta tanto esta relación?") y la IA responde
usando su carta natal como contexto real — no una respuesta genérica de
bola de cristal, sino conectada a su Sol, Luna, Ascendente y aspectos.

Mantiene memoria ligera de la conversación (las últimas preguntas y
respuestas) para que las preguntas de seguimiento tengan sentido, igual
que un chat real.
"""
import os
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "llama-3.3-70b-versatile"


def _construir_prompt(pregunta: str, carta_natal: dict, historial: list[dict] | None) -> str:
    sol = carta_natal["planetas"]["Sol"]
    luna = carta_natal["planetas"]["Luna"]
    ascendente = carta_natal["ascendente"]

    aspectos_texto = "; ".join(
        f"{a['planetas'][0]}-{a['planetas'][1]} en {a['aspecto']} ({a['naturaleza']})"
        for a in carta_natal["aspectos"][:4]
    ) or "sin aspectos exactos destacados"

    historial_texto = ""
    if historial:
        turnos = []
        for h in historial[-3:]:  # solo las últimas 3 preguntas, para no saturar el prompt
            turnos.append(f"Ella preguntó: {h.get('pregunta', '')}\nLe respondiste: {h.get('respuesta', '')}")
        historial_texto = "\n\nConversación previa en esta misma sesión:\n" + "\n\n".join(turnos)

    return f"""Eres el Oráculo Astral: un guía espiritual cálido, directo y honesto que responde
preguntas puntuales de la vida real usando la carta natal de la persona como contexto,
para una app en español dirigida a Latinoamérica. No das respuestas vagas de bola de
cristal — conectas tu respuesta con su carta natal real cuando sea relevante, y si la
pregunta no tiene relación astrológica clara, igual respondes con sabiduría y calidez,
sin forzar una conexión que no existe.

Su carta natal:
- Sol en {sol['signo']} (casa {sol['casa']}), Luna en {luna['signo']} (casa {luna['casa']}), Ascendente en {ascendente['signo']}
- Aspectos: {aspectos_texto}
{historial_texto}

Su pregunta ahora: "{pregunta}"

Responde en 2 a 3 párrafos cortos, cálidos y directos — como una conversación real, no
un discurso. No uses encabezados ni listas. Si la pregunta toca un tema serio de salud,
legal o financiero, puedes dar tu perspectiva espiritual pero sugiere con cuidado que
también busque a un profesional para eso específico, sin sonar a advertencia legal fría."""


def responder_pregunta(pregunta: str, carta_natal: dict, historial: list[dict] | None = None) -> str:
    """
    Genera la respuesta del oráculo a una pregunta libre de la persona.
    Requiere la variable de entorno GROQ_API_KEY (gratis en console.groq.com).
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Falta configurar GROQ_API_KEY en las variables de entorno del servidor.")

    prompt = _construir_prompt(pregunta, carta_natal, historial)

    respuesta = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": MODELO,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.85,
            "max_tokens": 450,
        },
        timeout=30,
    )
    if not respuesta.ok:
        raise RuntimeError(f"Groq rechazó la petición (código {respuesta.status_code}): {respuesta.text}")

    return respuesta.json()["choices"][0]["message"]["content"]
