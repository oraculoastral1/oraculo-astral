"""
Servicio de cálculo de carta natal usando Swiss Ephemeris.
Fase 2 · Ciudades reales + aspectos planetarios — Proyecto 09 · Oráculo Astral
"""
import swisseph as swe
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import TypedDict
from itertools import combinations

from app.services.ciudades import buscar_ciudad

PLANETAS = {
    "Sol": swe.SUN,
    "Luna": swe.MOON,
    "Mercurio": swe.MERCURY,
    "Venus": swe.VENUS,
    "Marte": swe.MARS,
    "Júpiter": swe.JUPITER,
    "Saturno": swe.SATURN,
    "Urano": swe.URANUS,
    "Neptuno": swe.NEPTUNE,
    "Plutón": swe.PLUTO,
}

SIGNOS = [
    "Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo",
    "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis",
]

# Aspectos: ángulo exacto entre dos planetas + margen de tolerancia (orbe)
ASPECTOS = {
    "Conjunción": {"angulo": 0, "orbe": 8, "naturaleza": "fusión de energías"},
    "Sextil": {"angulo": 60, "orbe": 4, "naturaleza": "oportunidad, facilidad"},
    "Cuadratura": {"angulo": 90, "orbe": 6, "naturaleza": "tensión, fricción productiva"},
    "Trígono": {"angulo": 120, "orbe": 6, "naturaleza": "armonía, talento natural"},
    "Oposición": {"angulo": 180, "orbe": 8, "naturaleza": "polaridad, necesidad de equilibrio"},
}


class PosicionPlaneta(TypedDict):
    signo: str
    grado: float
    casa: int


def _signo_desde_longitud(longitud: float) -> tuple[str, float]:
    indice_signo = int(longitud // 30)
    grado_en_signo = longitud % 30
    return SIGNOS[indice_signo], round(grado_en_signo, 2)


def _diferencia_angular(a: float, b: float) -> float:
    """Distancia angular más corta entre dos puntos del zodiaco (0-360°)."""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def _calcular_aspectos(posiciones: dict) -> list[dict]:
    """Revisa cada par de planetas y detecta si forman un aspecto reconocido."""
    aspectos_encontrados = []
    nombres_planetas = list(posiciones.keys())

    for p1, p2 in combinations(nombres_planetas, 2):
        angulo_real = _diferencia_angular(posiciones[p1]["_longitud"], posiciones[p2]["_longitud"])

        for nombre_aspecto, datos in ASPECTOS.items():
            diferencia = abs(angulo_real - datos["angulo"])
            if diferencia <= datos["orbe"]:
                aspectos_encontrados.append({
                    "planetas": [p1, p2],
                    "aspecto": nombre_aspecto,
                    "orbe_exacto": round(diferencia, 2),
                    "naturaleza": datos["naturaleza"],
                })
                break

    return aspectos_encontrados


def calcular_carta_natal(
    fecha: str,
    hora: str,
    ciudad: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    zona_horaria: str | None = None,
) -> dict:
    """
    Calcula la carta natal real a partir de fecha, hora y lugar de nacimiento.
    El lugar se puede dar como nombre de ciudad (recomendado) o como
    coordenadas + zona horaria manuales.
    """
    nombre_lugar = ciudad

    if ciudad:
        info_ciudad = buscar_ciudad(ciudad)
        if not info_ciudad:
            raise ValueError(
                "No tengo esa ciudad en mi lista todavía. "
                "Prueba con el nombre de una capital cercana, o envía lat/lon manualmente."
            )
        lat = info_ciudad["lat"]
        lon = info_ciudad["lon"]
        zona_horaria = info_ciudad["tz"]
        nombre_lugar = info_ciudad["nombre"]
    elif lat is None or lon is None or zona_horaria is None:
        raise ValueError("Debes enviar 'ciudad', o bien 'lat', 'lon' y 'zona_horaria'.")

    dt_local = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
    dt_local = dt_local.replace(tzinfo=ZoneInfo(zona_horaria))
    dt_utc = dt_local.astimezone(ZoneInfo("UTC"))

    hora_decimal_ut = dt_utc.hour + dt_utc.minute / 60
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hora_decimal_ut)

    casas, angulos = swe.houses(jd_ut, lat, lon, b'P')
    ascendente_signo, ascendente_grado = _signo_desde_longitud(angulos[0])
    medio_cielo_signo, medio_cielo_grado = _signo_desde_longitud(angulos[1])

    posiciones: dict[str, PosicionPlaneta] = {}
    for nombre, codigo in PLANETAS.items():
        resultado, _ = swe.calc_ut(jd_ut, codigo)
        longitud = resultado[0]
        signo, grado = _signo_desde_longitud(longitud)

        casa_planeta = 12
        for i in range(12):
            inicio = casas[i]
            fin = casas[(i + 1) % 12]
            if fin < inicio:
                if longitud >= inicio or longitud < fin:
                    casa_planeta = i + 1
                    break
            elif inicio <= longitud < fin:
                casa_planeta = i + 1
                break

        posiciones[nombre] = {"signo": signo, "grado": grado, "casa": casa_planeta, "_longitud": longitud}

    aspectos = _calcular_aspectos(posiciones)

    for datos_planeta in posiciones.values():
        datos_planeta.pop("_longitud", None)

    return {
        "lugar": nombre_lugar,
        "fecha_hora_local": f"{fecha} {hora}",
        "coordenadas": {"lat": lat, "lon": lon},
        "ascendente": {"signo": ascendente_signo, "grado": ascendente_grado},
        "medio_cielo": {"signo": medio_cielo_signo, "grado": medio_cielo_grado},
        "planetas": posiciones,
        "aspectos": aspectos,
    }
