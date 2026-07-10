"""
Motor de compatibilidad — Fase 7.

Compara los planetas de dos cartas natales entre sí (lo que en astrología
se llama "sinastría") y le pide a la IA que interprete esas conexiones
como la dinámica real entre dos personas — no solo "signo con signo".
"""
import os
import requests

from app.services.carta_natal import ASPECTOS, _diferencia_angular

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "llama-3.3-70b-versatile"


def calcular_aspectos_cruzados(planetas_a: dict, planetas_b: dict) -> list[dict]:
    """
    Compara cada planeta de la persona A contra cada planeta de la persona B
    y detecta los aspectos que forman entre sí (sinastría).
    """
    aspectos_encontrados = []

    for nombre_a, datos_a in planetas_a.items():
        for nombre_b, datos_b in planetas_b.items():
            angulo_real = _diferencia_angular(datos_a["longitud"], datos_b["longitud"])

            for nombre_aspecto, datos_aspecto in ASPECTOS.items():
                diferencia = abs(angulo_real - datos_aspecto["angulo"])
                if diferencia <= datos_aspecto["orbe"]:
                    aspectos_encontrados.append({
                        "planeta_persona_a": nombre_a,
                        "planeta_persona_b": nombre_b,
                        "aspecto": nombre_aspecto,
                        "orbe_exacto": round(diferencia, 2),
                        "naturaleza": datos_aspecto["naturaleza"],
                    })
                    break

    return aspectos_encontrados


def _construir_prompt(
    nombre_a: str, carta_a: dict, nombre_b: str, carta_b: dict, aspectos_cruzados: list[dict]
) -> str:
    sol_a, luna_a = carta_a["planetas"]["Sol"], carta_a["planetas"]["Luna"]
    sol_b, luna_b = carta_b["planetas"]["Sol"], carta_b["planetas"]["Luna"]

    # Priorizamos los aspectos entre los planetas más personales (Sol, Luna, Venus, Marte)
    planetas_clave = {"Sol", "Luna", "Venus", "Marte"}
    aspectos_relevantes = [
        a for a in aspectos_cruzados
        if a["planeta_persona_a"] in planetas_clave or a["planeta_persona_b"] in planetas_clave
    ][:6]

    aspectos_texto = "; ".join(
        f"{nombre_a}·{a['planeta_persona_a']} con {nombre_b}·{a['planeta_persona_b']} "
        f"en {a['aspecto']} ({a['naturaleza']})"
        for a in aspectos_relevantes
    ) or "sin aspectos cruzados exactos destacados"

    return f"""Eres un guía espiritual cálido y perspicaz que interpreta la compatibilidad
astrológica entre dos personas (sinastría) para una app en español dirigida a
Latinoamérica. Tu tono es honesto y equilibrado — mencionas tanto la química
natural como las fricciones reales, nunca solo cosas positivas de manera vacía.

{nombre_a}: Sol en {sol_a['signo']}, Luna en {luna_a['signo']}
{nombre_b}: Sol en {sol_b['signo']}, Luna en {luna_b['signo']}

Conexiones astrológicas entre ambas cartas: {aspectos_texto}

Escribe una lectura de compatibilidad de 3 a 4 párrafos cortos que:
1. Explique la dinámica central entre ambas personas, basada en las conexiones reales de sus cartas
2. Mencione tanto una fortaleza natural de la relación como un área de fricción o aprendizaje
3. Cierre con un consejo práctico para que la relación (de pareja, amistad o trabajo) fluya mejor

No uses encabezados ni listas. Escribe en prosa fluida, refiriéndote a {nombre_a} y {nombre_b}
por nombre."""


def generar_lectura_compatibilidad(nombre_a: str, carta_a: dict, nombre_b: str, carta_b: dict) -> dict:
    """
    Genera la lectura de compatibilidad completa entre dos personas.
    Requiere la variable de entorno GROQ_API_KEY (gratis en console.groq.com).
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "Falta configurar GROQ_API_KEY en las variables de entorno del servidor."
        )

    aspectos_cruzados = calcular_aspectos_cruzados(carta_a["planetas"], carta_b["planetas"])
    prompt = _construir_prompt(nombre_a, carta_a, nombre_b, carta_b, aspectos_cruzados)

    respuesta = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": MODELO,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 500,
        },
        timeout=30,
    )
    if not respuesta.ok:
        raise RuntimeError(f"Groq rechazó la petición (código {respuesta.status_code}): {respuesta.text}")

    texto = respuesta.json()["choices"][0]["message"]["content"]

    return {
        "aspectos_cruzados": aspectos_cruzados,
        "lectura": texto,
    }
