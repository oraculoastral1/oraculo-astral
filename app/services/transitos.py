"""
Motor de tránsitos planetarios — Mejora #1.

Hasta ahora, la lectura diaria se basaba en la carta natal (fija) + numerología
(fija) + una carta de tarot al azar. Lo que faltaba era el ingrediente que usan
los astrólogos de verdad: dónde están los planetas HOY, comparados contra la
carta de nacimiento de la persona. Eso es un "tránsito", y es lo que hace que
la lectura de mañana sea genuinamente distinta a la de hoy — por motivos
astronómicos reales, no solo porque salió otra carta de tarot al azar.

Reutiliza exactamente la misma lógica de aspectos ya construida en
carta_natal.py — un tránsito es matemáticamente lo mismo que la sinastría de
compatibilidad, pero comparando "el cielo de hoy" contra la carta natal de
una sola persona, en vez de contra la carta de otra persona.
"""
from datetime import datetime, timezone
import swisseph as swe

from app.services.carta_natal import PLANETAS, ASPECTOS, _signo_desde_longitud, _diferencia_angular

# Los planetas lentos (Júpiter en adelante) son los que más importan en
# tránsitos porque marcan tendencias de semanas o meses, no solo del día.
PLANETAS_TRANSITO_CLAVE = {"Júpiter", "Saturno", "Urano", "Neptuno", "Plutón"}
# Los planetas personales de la persona son los que más se sienten cuando
# un tránsito los toca.
PLANETAS_NATALES_CLAVE = {"Sol", "Luna", "Ascendente", "Mercurio", "Venus", "Marte"}


def obtener_posiciones_actuales() -> dict:
    """
    Calcula dónde está cada planeta EN ESTE MOMENTO (hora UTC), sin
    depender de ninguna ubicación — los tránsitos son iguales para
    todo el planeta Tierra, solo cambian según la carta natal de cada quien.
    """
    ahora_utc = datetime.now(timezone.utc)
    jd_ut = swe.julday(
        ahora_utc.year, ahora_utc.month, ahora_utc.day,
        ahora_utc.hour + ahora_utc.minute / 60,
    )

    posiciones = {}
    for nombre, codigo in PLANETAS.items():
        resultado, _ = swe.calc_ut(jd_ut, codigo)
        longitud = resultado[0]
        signo, grado = _signo_desde_longitud(longitud)
        posiciones[nombre] = {"signo": signo, "grado": grado, "longitud": longitud}

    return posiciones


def calcular_transitos_del_dia(carta_natal: dict) -> list[dict]:
    """
    Compara los planetas de hoy contra la carta natal de la persona,
    y devuelve solo los tránsitos relevantes: los que tocan alguno de
    sus planetas personales o su ascendente, priorizando los planetas
    lentos (que marcan tendencias, no ruido pasajero).
    """
    posiciones_hoy = obtener_posiciones_actuales()
    planetas_natales = dict(carta_natal["planetas"])
    planetas_natales["Ascendente"] = {"longitud": _longitud_desde_signo_grado(
        carta_natal["ascendente"]["signo"], carta_natal["ascendente"]["grado"]
    )}

    transitos_encontrados = []

    for planeta_transitando, datos_transito in posiciones_hoy.items():
        if planeta_transitando not in PLANETAS_TRANSITO_CLAVE:
            continue  # ignoramos planetas rápidos (Sol, Luna, Mercurio, Venus, Marte transitando) — cambian a diario y generan ruido, no tendencia

        for planeta_natal, datos_natal in planetas_natales.items():
            if planeta_natal not in PLANETAS_NATALES_CLAVE:
                continue

            angulo_real = _diferencia_angular(datos_transito["longitud"], datos_natal["longitud"])

            for nombre_aspecto, datos_aspecto in ASPECTOS.items():
                # Para tránsitos usamos un orbe más angosto (más exacto) que en
                # la carta natal, porque aquí buscamos el momento preciso, no
                # una tendencia amplia de toda la vida.
                orbe_transito = min(datos_aspecto["orbe"], 3)
                diferencia = abs(angulo_real - datos_aspecto["angulo"])
                if diferencia <= orbe_transito:
                    transitos_encontrados.append({
                        "planeta_en_transito": planeta_transitando,
                        "planeta_natal": planeta_natal,
                        "aspecto": nombre_aspecto,
                        "orbe_exacto": round(diferencia, 2),
                        "naturaleza": datos_aspecto["naturaleza"],
                    })
                    break

    return transitos_encontrados


def _longitud_desde_signo_grado(signo: str, grado: float) -> float:
    """Reconstruye la longitud absoluta (0-360°) a partir de signo + grado dentro del signo."""
    from app.services.carta_natal import SIGNOS
    return SIGNOS.index(signo) * 30 + grado
