"""
Base de datos de ciudades para convertir "Bogotá" en coordenadas + zona horaria,
sin depender de un servicio externo (más rápido, gratis, sin límites de uso).

Cada ciudad usa el nombre de zona horaria IANA (ej: "America/Bogota"), que Python
sabe convertir a UTC correctamente incluso considerando cambios históricos de
horario de verano — esto es más preciso que pedirle al usuario un offset fijo.
"""

CIUDADES = {
    "bogota": {"nombre": "Bogotá, Colombia", "lat": 4.7110, "lon": -74.0721, "tz": "America/Bogota"},
    "medellin": {"nombre": "Medellín, Colombia", "lat": 6.2442, "lon": -75.5812, "tz": "America/Bogota"},
    "cali": {"nombre": "Cali, Colombia", "lat": 3.4516, "lon": -76.5320, "tz": "America/Bogota"},
    "barranquilla": {"nombre": "Barranquilla, Colombia", "lat": 10.9639, "lon": -74.7964, "tz": "America/Bogota"},
    "ciudad de mexico": {"nombre": "Ciudad de México, México", "lat": 19.4326, "lon": -99.1332, "tz": "America/Mexico_City"},
    "guadalajara": {"nombre": "Guadalajara, México", "lat": 20.6597, "lon": -103.3496, "tz": "America/Mexico_City"},
    "monterrey": {"nombre": "Monterrey, México", "lat": 25.6866, "lon": -100.3161, "tz": "America/Monterrey"},
    "buenos aires": {"nombre": "Buenos Aires, Argentina", "lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},
    "cordoba": {"nombre": "Córdoba, Argentina", "lat": -31.4201, "lon": -64.1888, "tz": "America/Argentina/Cordoba"},
    "santiago": {"nombre": "Santiago, Chile", "lat": -33.4489, "lon": -70.6693, "tz": "America/Santiago"},
    "lima": {"nombre": "Lima, Perú", "lat": -12.0464, "lon": -77.0428, "tz": "America/Lima"},
    "quito": {"nombre": "Quito, Ecuador", "lat": -0.1807, "lon": -78.4678, "tz": "America/Guayaquil"},
    "guayaquil": {"nombre": "Guayaquil, Ecuador", "lat": -2.1709, "lon": -79.9224, "tz": "America/Guayaquil"},
    "caracas": {"nombre": "Caracas, Venezuela", "lat": 10.4806, "lon": -66.9036, "tz": "America/Caracas"},
    "montevideo": {"nombre": "Montevideo, Uruguay", "lat": -34.9011, "lon": -56.1645, "tz": "America/Montevideo"},
    "asuncion": {"nombre": "Asunción, Paraguay", "lat": -25.2637, "lon": -57.5759, "tz": "America/Asuncion"},
    "la paz": {"nombre": "La Paz, Bolivia", "lat": -16.5000, "lon": -68.1500, "tz": "America/La_Paz"},
    "san jose": {"nombre": "San José, Costa Rica", "lat": 9.9281, "lon": -84.0907, "tz": "America/Costa_Rica"},
    "panama": {"nombre": "Ciudad de Panamá, Panamá", "lat": 8.9824, "lon": -79.5199, "tz": "America/Panama"},
    "san salvador": {"nombre": "San Salvador, El Salvador", "lat": 13.6929, "lon": -89.2182, "tz": "America/El_Salvador"},
    "tegucigalpa": {"nombre": "Tegucigalpa, Honduras", "lat": 14.0723, "lon": -87.1921, "tz": "America/Tegucigalpa"},
    "managua": {"nombre": "Managua, Nicaragua", "lat": 12.1364, "lon": -86.2514, "tz": "America/Managua"},
    "guatemala": {"nombre": "Ciudad de Guatemala, Guatemala", "lat": 14.6349, "lon": -90.5069, "tz": "America/Guatemala"},
    "santo domingo": {"nombre": "Santo Domingo, Rep. Dominicana", "lat": 18.4861, "lon": -69.9312, "tz": "America/Santo_Domingo"},
    "san juan": {"nombre": "San Juan, Puerto Rico", "lat": 18.4655, "lon": -66.1057, "tz": "America/Puerto_Rico"},
    "la habana": {"nombre": "La Habana, Cuba", "lat": 23.1136, "lon": -82.3666, "tz": "America/Havana"},
    "madrid": {"nombre": "Madrid, España", "lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid"},
    "miami": {"nombre": "Miami, Estados Unidos", "lat": 25.7617, "lon": -80.1918, "tz": "America/New_York"},
}


def buscar_ciudad(nombre_ciudad: str) -> dict | None:
    """Busca una ciudad de forma flexible (sin importar tildes/mayúsculas)."""
    clave = (
        nombre_ciudad.strip().lower()
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u")
    )
    return CIUDADES.get(clave)


def listar_ciudades() -> list[str]:
    return sorted(c["nombre"] for c in CIUDADES.values())
