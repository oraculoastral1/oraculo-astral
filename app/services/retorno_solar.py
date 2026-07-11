"""
Motor de retorno solar — Mejora #6.

El "retorno solar" es una técnica astrológica real: el momento exacto
(no solo el día, sino la hora y el minuto) en que el Sol vuelve a estar
en la misma posición exacta del zodiaco que tenía cuando naciste. Marca
el inicio de tu "año astral" personal, y una carta calculada para ese
instante revela los temas centrales del año que empieza.

A diferencia de la fecha de cumpleaños (que es aproximada, basada en el
calendario), el retorno solar real puede caer horas antes o después de
la medianoche de tu cumpleaños — por eso hay que *encontrarlo*, no solo
calcularlo directamente.

Nota honesta sobre el alcance: un retorno solar profesional se calcula
con la ubicación donde la persona VIVE ese año (no donde nació), porque
el lugar cambia las casas de la carta. Como no recolectamos la ubicación
actual de la persona, usamos su ciudad de nacimiento como aproximación
razonable — el resultado sigue siendo válido, pero un astrólogo profesional
ajustaría esto con tu ciudad actual si te has mudado.
"""
from datetime import datetime, timezone
from itertools import combinations
import swisseph as swe

from app.services.carta_natal import (
    PLANETAS, ASPECTOS, SIGNOS, _signo_desde_longitud, _diferencia_angular,
)

GRADOS_POR_DIA_SOL = 0.9856  # velocidad media del Sol en el zodiaco


def _diferencia_con_signo(objetivo: float, actual: float) -> float:
    """Como _diferencia_angular, pero conserva el signo (para saber hacia dónde mover el tiempo)."""
    return (objetivo - actual + 180) % 360 - 180


def _encontrar_momento_retorno(sol_natal_longitud: float, fecha_nacimiento: str) -> tuple[float, int]:
    """
    Busca el instante (día juliano UT) en que el Sol transita exactamente
    la longitud natal, en el año de retorno más reciente (el cumpleaños ya
    pasado o de hoy, no uno futuro). Devuelve (jd_ut, año_de_retorno).
    """
    nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d")
    hoy = datetime.now(timezone.utc)

    anio_objetivo = hoy.year
    cumple_este_anio = (nacimiento.month, nacimiento.day)
    if (hoy.month, hoy.day) < cumple_este_anio:
        anio_objetivo -= 1

    # Punto de partida: mismo mes/día de nacimiento, mediodía UTC, del año objetivo
    dia = nacimiento.day
    if nacimiento.month == 2 and nacimiento.day == 29 and not _es_bisiesto(anio_objetivo):
        dia = 28  # cumpleaños del 29 de febrero en año no bisiesto
    estimado = datetime(anio_objetivo, nacimiento.month, dia, 12, 0, tzinfo=timezone.utc)
    jd = swe.julday(estimado.year, estimado.month, estimado.day, 12.0)

    # Afinamos con iteraciones (el Sol se mueve a velocidad casi constante,
    # así que converge muy rápido — 4 vueltas son de sobra para precisión al minuto)
    for _ in range(4):
        resultado, _ = swe.calc_ut(jd, swe.SUN)
        longitud_actual = resultado[0]
        diferencia = _diferencia_con_signo(sol_natal_longitud, longitud_actual)
        jd += diferencia / GRADOS_POR_DIA_SOL

    return jd, anio_objetivo


def _es_bisiesto(anio: int) -> bool:
    return anio % 4 == 0 and (anio % 100 != 0 or anio % 400 == 0)


def _calcular_aspectos_cruzados(planetas_a: dict, planetas_b: dict) -> list[dict]:
    """Compara los planetas del retorno solar contra los planetas natales."""
    aspectos = []
    for nombre_a, datos_a in planetas_a.items():
        for nombre_b, datos_b in planetas_b.items():
            angulo_real = _diferencia_angular(datos_a["longitud"], datos_b["longitud"])
            for nombre_aspecto, datos_aspecto in ASPECTOS.items():
                diferencia = abs(angulo_real - datos_aspecto["angulo"])
                if diferencia <= datos_aspecto["orbe"]:
                    aspectos.append({
                        "planeta_retorno": nombre_a,
                        "planeta_natal": nombre_b,
                        "aspecto": nombre_aspecto,
                        "naturaleza": datos_aspecto["naturaleza"],
                    })
                    break
    return aspectos


def calcular_retorno_solar(carta_natal: dict, lat: float, lon: float) -> dict:
    """
    Calcula la carta completa del retorno solar más reciente de una persona:
    el momento exacto, el ascendente de ese momento, y cómo se relacionan
    sus planetas con los de la carta natal.
    """
    sol_natal_longitud = carta_natal["planetas"]["Sol"]["longitud"]
    fecha_nacimiento = carta_natal["fecha_hora_local"].split(" ")[0]

    jd, anio_retorno = _encontrar_momento_retorno(sol_natal_longitud, fecha_nacimiento)

    casas, angulos = swe.houses(jd, lat, lon, b'P')
    ascendente_signo, ascendente_grado = _signo_desde_longitud(angulos[0])

    planetas_retorno = {}
    for nombre, codigo in PLANETAS.items():
        resultado, _ = swe.calc_ut(jd, codigo)
        longitud = resultado[0]
        signo, grado = _signo_desde_longitud(longitud)

        casa_planeta = 12
        for i in range(12):
            inicio, fin = casas[i], casas[(i + 1) % 12]
            if fin < inicio:
                if longitud >= inicio or longitud < fin:
                    casa_planeta = i + 1
                    break
            elif inicio <= longitud < fin:
                casa_planeta = i + 1
                break

        planetas_retorno[nombre] = {"signo": signo, "grado": grado, "casa": casa_planeta, "longitud": longitud}

    aspectos_cruzados = _calcular_aspectos_cruzados(planetas_retorno, carta_natal["planetas"])

    fecha_exacta = swe.revjul(jd)  # (año, mes, día, hora_decimal_UT)

    return {
        "anio_retorno": anio_retorno,
        "fecha_hora_exacta_utc": f"{fecha_exacta[0]:04d}-{fecha_exacta[1]:02d}-{fecha_exacta[2]:02d} "
                                  f"{int(fecha_exacta[3]):02d}:{int((fecha_exacta[3] % 1) * 60):02d} UTC",
        "ascendente_retorno": {"signo": ascendente_signo, "grado": ascendente_grado},
        "sol_casa_retorno": planetas_retorno["Sol"]["casa"],
        "planetas": planetas_retorno,
        "aspectos_cruzados": aspectos_cruzados,
    }


# ---------- Interpretación con IA ----------
import os
import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODELO = "llama-3.3-70b-versatile"

CASAS_TEMAS = {
    1: "tu identidad y cómo te presentas al mundo", 2: "tus recursos, tu dinero y tu autoestima",
    3: "tu comunicación, tus estudios y tu entorno cercano", 4: "tu hogar, tu familia y tus raíces",
    5: "tu creatividad, el amor y el disfrute", 6: "tu trabajo diario, tu salud y tus rutinas",
    7: "tus relaciones de pareja y sociedades", 8: "las transformaciones profundas y lo compartido",
    9: "los viajes, el aprendizaje superior y tu filosofía de vida", 10: "tu carrera y tu lugar público",
    11: "tus amistades, tus proyectos colectivos y tus sueños a futuro", 12: "tu mundo interior y el descanso",
}


def _construir_prompt_retorno(nombre: str, anio_retorno: int, datos_retorno: dict, carta_natal: dict) -> str:
    ascendente = datos_retorno["ascendente_retorno"]
    tema_casa_sol = CASAS_TEMAS.get(datos_retorno["sol_casa_retorno"], "tu camino personal")

    planetas_clave = {"Sol", "Luna", "Ascendente"}
    aspectos_relevantes = [
        a for a in datos_retorno["aspectos_cruzados"]
        if a["planeta_retorno"] in planetas_clave or a["planeta_natal"] in planetas_clave
    ][:5]
    aspectos_texto = "; ".join(
        f"{a['planeta_retorno']} del año con {a['planeta_natal']} natal en {a['aspecto']} ({a['naturaleza']})"
        for a in aspectos_relevantes
    ) or "sin aspectos destacados entre el año nuevo y tu carta de siempre"

    return f"""Eres un guía espiritual cálido y sabio, experto en la técnica astrológica del
retorno solar, escribiendo para una app en español dirigida a Latinoamérica.

{nombre} acaba de cumplir años. Es el momento de su retorno solar {anio_retorno} —
el instante exacto en que el Sol volvió a su posición de nacimiento, marcando el
inicio de su nuevo año astral (válido hasta su próximo cumpleaños).

Datos de su año que comienza:
- Ascendente del año: {ascendente['signo']} (esto marca el tono general del año)
- El Sol de este año cae en la casa {datos_retorno['sol_casa_retorno']} de su carta de retorno,
  relacionada con {tema_casa_sol} — este es el área central donde brillará este año
- Conexiones entre el cielo de este cumpleaños y su carta de nacimiento: {aspectos_texto}

Escribe una lectura de "año astral" de 4 párrafos cortos que:
1. Dé la bienvenida al nuevo año astral con calidez, mencionando que este momento exacto es único de este cumpleaños
2. Explique el tema central del año a partir del ascendente y la casa donde cae el Sol
3. Profundice en las conexiones con su carta natal — qué se activa, qué fluye, qué pide atención
4. Cierre con una intención o consejo para aprovechar este nuevo ciclo

No uses encabezados ni listas. Escribe en prosa fluida y personal, como un regalo de cumpleaños."""


def generar_lectura_retorno_solar(nombre: str, carta_natal: dict, lat: float, lon: float) -> dict:
    """
    Calcula el retorno solar completo y genera su interpretación con IA.
    Requiere la variable de entorno GROQ_API_KEY (gratis en console.groq.com).
    """
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Falta configurar GROQ_API_KEY en las variables de entorno del servidor.")

    datos_retorno = calcular_retorno_solar(carta_natal, lat, lon)
    prompt = _construir_prompt_retorno(nombre, datos_retorno["anio_retorno"], datos_retorno, carta_natal)

    respuesta = requests.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": MODELO,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 600,
        },
        timeout=30,
    )
    if not respuesta.ok:
        raise RuntimeError(f"Groq rechazó la petición (código {respuesta.status_code}): {respuesta.text}")

    texto = respuesta.json()["choices"][0]["message"]["content"]

    return {
        "anio_retorno": datos_retorno["anio_retorno"],
        "fecha_hora_exacta_utc": datos_retorno["fecha_hora_exacta_utc"],
        "ascendente_retorno": datos_retorno["ascendente_retorno"],
        "sol_casa_retorno": datos_retorno["sol_casa_retorno"],
        "lectura": texto,
    }
