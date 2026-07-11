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
    # Valle de Aburrá (área metropolitana de Medellín) — muy comunes como ciudad de nacimiento
    "bello": {"nombre": "Bello, Colombia", "lat": 6.3373, "lon": -75.5580, "tz": "America/Bogota"},
    "itagui": {"nombre": "Itagüí, Colombia", "lat": 6.1719, "lon": -75.6122, "tz": "America/Bogota"},
    "envigado": {"nombre": "Envigado, Colombia", "lat": 6.1731, "lon": -75.5854, "tz": "America/Bogota"},
    "sabaneta": {"nombre": "Sabaneta, Colombia", "lat": 6.1500, "lon": -75.6167, "tz": "America/Bogota"},
    "la estrella": {"nombre": "La Estrella, Colombia", "lat": 6.1517, "lon": -75.6428, "tz": "America/Bogota"},
    "copacabana": {"nombre": "Copacabana, Colombia", "lat": 6.3489, "lon": -75.5083, "tz": "America/Bogota"},
    "caldas": {"nombre": "Caldas, Colombia", "lat": 6.0917, "lon": -75.6347, "tz": "America/Bogota"},
    "girardota": {"nombre": "Girardota, Colombia", "lat": 6.3778, "lon": -75.4444, "tz": "America/Bogota"},
    # Otras ciudades importantes de Colombia
    "cartagena": {"nombre": "Cartagena, Colombia", "lat": 10.3910, "lon": -75.4794, "tz": "America/Bogota"},
    "bucaramanga": {"nombre": "Bucaramanga, Colombia", "lat": 7.1193, "lon": -73.1227, "tz": "America/Bogota"},
    "pereira": {"nombre": "Pereira, Colombia", "lat": 4.8087, "lon": -75.6906, "tz": "America/Bogota"},
    "manizales": {"nombre": "Manizales, Colombia", "lat": 5.0689, "lon": -75.5174, "tz": "America/Bogota"},
    "santa marta": {"nombre": "Santa Marta, Colombia", "lat": 11.2408, "lon": -74.1990, "tz": "America/Bogota"},
    "cucuta": {"nombre": "Cúcuta, Colombia", "lat": 7.8939, "lon": -72.5078, "tz": "America/Bogota"},
    "ibague": {"nombre": "Ibagué, Colombia", "lat": 4.4389, "lon": -75.2322, "tz": "America/Bogota"},
    "pasto": {"nombre": "Pasto, Colombia", "lat": 1.2136, "lon": -77.2811, "tz": "America/Bogota"},
    "villavicencio": {"nombre": "Villavicencio, Colombia", "lat": 4.1420, "lon": -73.6266, "tz": "America/Bogota"},
    "armenia": {"nombre": "Armenia, Colombia", "lat": 4.5339, "lon": -75.6811, "tz": "America/Bogota"},
    "neiva": {"nombre": "Neiva, Colombia", "lat": 2.9273, "lon": -75.2819, "tz": "America/Bogota"},
    "popayan": {"nombre": "Popayán, Colombia", "lat": 2.4448, "lon": -76.6147, "tz": "America/Bogota"},
    "monteria": {"nombre": "Montería, Colombia", "lat": 8.7479, "lon": -75.8814, "tz": "America/Bogota"},
    "valledupar": {"nombre": "Valledupar, Colombia", "lat": 10.4631, "lon": -73.2532, "tz": "America/Bogota"},
    "sincelejo": {"nombre": "Sincelejo, Colombia", "lat": 9.3047, "lon": -75.3978, "tz": "America/Bogota"},
    "tunja": {"nombre": "Tunja, Colombia", "lat": 5.5353, "lon": -73.3678, "tz": "America/Bogota"},
    "riohacha": {"nombre": "Riohacha, Colombia", "lat": 11.5444, "lon": -72.9072, "tz": "America/Bogota"},
    # México, resto de LATAM y España
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
        .replace("ó", "o").replace("ú", "u").replace("ü", "u")
    )
    return CIUDADES.get(clave)


def listar_ciudades() -> list[str]:
    return sorted(c["nombre"] for c in CIUDADES.values())
