"""
Servicio de cálculo de carta natal usando Swiss Ephemeris.
Fase 1 · Fundamentos técnicos — Proyecto 09 · Oráculo IA
"""
import swisseph as swe
from datetime import datetime
from typing import TypedDict

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


class PosicionPlaneta(TypedDict):
    signo: str
    grado: float
    casa: int


def _signo_desde_longitud(longitud: float) -> tuple[str, float]:
    indice_signo = int(longitud // 30)
    grado_en_signo = longitud % 30
    return SIGNOS[indice_signo], round(grado_en_signo, 2)


def calcular_carta_natal(
    fecha: str,      # "YYYY-MM-DD"
    hora: str,       # "HH:MM" en hora local
    lat: float,
    lon: float,
    zona_horaria_utc_offset: float = 0.0,
) -> dict:
    """
    Calcula la carta natal real a partir de fecha, hora y lugar de nacimiento.
    Devuelve posiciones planetarias, casas astrológicas y ascendente.
    """
    dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")

    # Convertir a hora universal (UT) restando el offset de zona horaria
    hora_decimal_ut = (dt.hour + dt.minute / 60) - zona_horaria_utc_offset

    # Día juliano en UT — la unidad de tiempo que usa Swiss Ephemeris
    jd_ut = swe.julday(dt.year, dt.month, dt.day, hora_decimal_ut)

    # Casas astrológicas (sistema Placidus) + Ascendente/Medio Cielo
    casas, angulos = swe.houses(jd_ut, lat, lon, b'P')
    ascendente_signo, ascendente_grado = _signo_desde_longitud(angulos[0])
    medio_cielo_signo, medio_cielo_grado = _signo_desde_longitud(angulos[1])

    posiciones: dict[str, PosicionPlaneta] = {}
    for nombre, codigo in PLANETAS.items():
        resultado, _ = swe.calc_ut(jd_ut, codigo)
        longitud = resultado[0]
        signo, grado = _signo_desde_longitud(longitud)

        # Determinar en qué casa cae el planeta
        casa_planeta = 12
        for i in range(12):
            inicio = casas[i]
            fin = casas[(i + 1) % 12]
            if fin < inicio:  # cruza los 360°/0°
                if longitud >= inicio or longitud < fin:
                    casa_planeta = i + 1
                    break
            elif inicio <= longitud < fin:
                casa_planeta = i + 1
                break

        posiciones[nombre] = {"signo": signo, "grado": grado, "casa": casa_planeta}

    return {
        "fecha_hora_local": f"{fecha} {hora}",
        "coordenadas": {"lat": lat, "lon": lon},
        "ascendente": {"signo": ascendente_signo, "grado": ascendente_grado},
        "medio_cielo": {"signo": medio_cielo_signo, "grado": medio_cielo_grado},
        "planetas": posiciones,
    }
