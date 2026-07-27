"""
Motor de ciudades — ahora con los 1.122 municipios oficiales de Colombia
(fuente: DIVIPOLA, DANE — división político-administrativa oficial),
en vez de una lista corta hecha a mano. Antes, ciudades reales como
Yolombó (Antioquia) simplemente no existían en el sistema.

Como 66 nombres de municipio se repiten en más de un departamento
(ej: "Armenia" existe en Quindío Y en Antioquia), el nombre que se
muestra y se busca es "Municipio, Departamento" para Colombia — nunca
hay ambigüedad. Para las capitales de departamento cuyo nombre coincide
con un municipio pequeño y poco conocido (Armenia, Florencia), se
prioriza la capital al buscar solo por el nombre simple.
"""
import json
import os

_RUTA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "municipios_colombia.json")

with open(_RUTA_JSON, encoding="utf-8") as _f:
    _MUNICIPIOS_COLOMBIA = json.load(_f)


def _normalizar(texto: str) -> str:
    return (
        texto.strip().lower()
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u").replace("ü", "u").replace("ñ", "n")
    )


_ALIAS_COMUNES = {
    "cali": "santiago de cali",
    "cartagena": "cartagena de indias",
    "cucuta": "san jose de cucuta",
    "buga": "guadalajara de buga",
    "tumaco": "san andres de tumaco",
}

_PRIORIDAD_CAPITALES = {
    "armenia": "armenia, quindio",
    "florencia": "florencia, caqueta",
}

CIUDADES_INTERNACIONAL = {
    "ciudad de mexico": {"nombre": "Ciudad de México, México", "lat": 19.4326, "lon": -99.1332, "tz": "America/Mexico_City"},
    "guadalajara": {"nombre": "Guadalajara, México", "lat": 20.6597, "lon": -103.3496, "tz": "America/Mexico_City"},
    "monterrey": {"nombre": "Monterrey, México", "lat": 25.6866, "lon": -100.3161, "tz": "America/Monterrey"},
    "buenos aires": {"nombre": "Buenos Aires, Argentina", "lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
    "cordoba argentina": {"nombre": "Córdoba, Argentina", "lat": -31.4201, "lon": -64.1888, "tz": "America/Argentina/Cordoba"},
    "santiago": {"nombre": "Santiago, Chile", "lat": -33.4489, "lon": -70.6693, "tz": "America/Santiago"},
    "lima": {"nombre": "Lima, Perú", "lat": -12.0464, "lon": -77.0428, "tz": "America/Lima"},
    "quito": {"nombre": "Quito, Ecuador", "lat": -0.1807, "lon": -78.4678, "tz": "America/Guayaquil"},
    "guayaquil": {"nombre": "Guayaquil, Ecuador", "lat": -2.1709, "lon": -79.9224, "tz": "America/Guayaquil"},
    "caracas": {"nombre": "Caracas, Venezuela", "lat": 10.4806, "lon": -66.9036, "tz": "America/Caracas"},
    "montevideo": {"nombre": "Montevideo, Uruguay", "lat": -34.9011, "lon": -56.1645, "tz": "America/Montevideo"},
    "asuncion": {"nombre": "Asunción, Paraguay", "lat": -25.2637, "lon": -57.5759, "tz": "America/Asuncion"},
    "la paz": {"nombre": "La Paz, Bolivia", "lat": -16.5000, "lon": -68.1500, "tz": "America/La_Paz"},
    "san jose costa rica": {"nombre": "San José, Costa Rica", "lat": 9.9281, "lon": -84.0907, "tz": "America/Costa_Rica"},
    "panama": {"nombre": "Ciudad de Panamá, Panamá", "lat": 8.9824, "lon": -79.5199, "tz": "America/Panama"},
    "san salvador": {"nombre": "San Salvador, El Salvador", "lat": 13.6929, "lon": -89.2182, "tz": "America/El_Salvador"},
    "tegucigalpa": {"nombre": "Tegucigalpa, Honduras", "lat": 14.0723, "lon": -87.1921, "tz": "America/Tegucigalpa"},
    "managua": {"nombre": "Managua, Nicaragua", "lat": 12.1364, "lon": -86.2514, "tz": "America/Managua"},
    "ciudad de guatemala": {"nombre": "Ciudad de Guatemala, Guatemala", "lat": 14.6349, "lon": -90.5069, "tz": "America/Guatemala"},
    "santo domingo": {"nombre": "Santo Domingo, Rep. Dominicana", "lat": 18.4861, "lon": -69.9312, "tz": "America/Santo_Domingo"},
    "san juan puerto rico": {"nombre": "San Juan, Puerto Rico", "lat": 18.4655, "lon": -66.1057, "tz": "America/Puerto_Rico"},
    "la habana": {"nombre": "La Habana, Cuba", "lat": 23.1136, "lon": -82.3666, "tz": "America/Havana"},
    "madrid": {"nombre": "Madrid, España", "lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid"},
    "barcelona": {"nombre": "Barcelona, España", "lat": 41.3851, "lon": 2.1734, "tz": "Europe/Madrid"},
    "miami": {"nombre": "Miami, Estados Unidos", "lat": 25.7617, "lon": -80.1918, "tz": "America/New_York"},
    "new york": {"nombre": "Nueva York, Estados Unidos", "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},
}

_CONTEO_NOMBRES: dict[str, int] = {}
for _m in _MUNICIPIOS_COLOMBIA:
    _clave = _normalizar(_m["municipio"])
    _CONTEO_NOMBRES[_clave] = _CONTEO_NOMBRES.get(_clave, 0) + 1

_COLOMBIA_COMPLETO: dict[str, dict] = {}
_COLOMBIA_SIMPLE: dict[str, dict] = {}

for _m in _MUNICIPIOS_COLOMBIA:
    _datos = {
        "nombre": f"{_m['municipio']}, {_m['departamento']}",
        "lat": _m["lat"],
        "lon": _m["lon"],
        "tz": "America/Bogota",
    }
    _clave_municipio = _normalizar(_m["municipio"])
    _clave_completa = _normalizar(f"{_m['municipio']}, {_m['departamento']}")
    _COLOMBIA_COMPLETO[_clave_completa] = _datos
    if _CONTEO_NOMBRES[_clave_municipio] == 1:
        _COLOMBIA_SIMPLE[_clave_municipio] = _datos


def buscar_ciudad(nombre_ciudad: str) -> dict | None:
    """
    Busca una ciudad de forma flexible (sin importar tildes/mayúsculas).
    Para Colombia, acepta tanto "Municipio, Departamento" (siempre exacto)
    como solo "Municipio" (si ese nombre no se repite en otro departamento,
    o si es una de las capitales priorizadas).
    """
    clave = _normalizar(nombre_ciudad)

    if clave in _ALIAS_COMUNES:
        clave = _ALIAS_COMUNES[clave]

    if clave in _COLOMBIA_COMPLETO:
        return _COLOMBIA_COMPLETO[clave]
    if clave in _COLOMBIA_SIMPLE:
        return _COLOMBIA_SIMPLE[clave]
    if clave in _PRIORIDAD_CAPITALES:
        return _COLOMBIA_COMPLETO[_PRIORIDAD_CAPITALES[clave]]
    if clave in CIUDADES_INTERNACIONAL:
        return CIUDADES_INTERNACIONAL[clave]

    return None


def es_nombre_ambiguo(nombre_ciudad: str) -> bool:
    """Dice si un nombre de municipio (sin departamento) existe en más de un departamento."""
    clave = _normalizar(nombre_ciudad)
    return _CONTEO_NOMBRES.get(clave, 0) > 1


def listar_ciudades() -> list[str]:
    """
    Devuelve todos los nombres para mostrar en la lista de sugerencias del
    formulario — 1.122 municipios de Colombia + ciudades internacionales.
    """
    nombres_colombia = sorted({d["nombre"] for d in _COLOMBIA_COMPLETO.values()})
    nombres_internacional = sorted(d["nombre"] for d in CIUDADES_INTERNACIONAL.values())
    return nombres_colombia + nombres_internacional
