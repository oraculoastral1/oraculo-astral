"""
Motor de límites de uso diario — evita que una sola cuenta agote los
créditos de IA generando cientos de peticiones seguidas (por error o
mala intención). Los límites son generosos para uso real, no para
frenar a nadie honesto.
"""
import os
from datetime import date
import requests

LIMITES_POR_DIA = {
    "lectura_diaria": 5,
    "suenos": 10,
    "audio": 5,
    "compatibilidad": 5,
    "oraculo_chat": 20,
    "retorno_solar": 3,
}


def _config_supabase() -> tuple[str, dict]:
    url_base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    clave = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url_base or not clave:
        raise RuntimeError("Faltan configurar SUPABASE_URL y SUPABASE_SERVICE_KEY en las variables de entorno.")
    headers = {
        "apikey": clave, "Authorization": f"Bearer {clave}",
        "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates",
    }
    return f"{url_base}/rest/v1/uso_diario", headers


def verificar_y_registrar_uso(usuario_id: str, accion: str) -> None:
    """
    Revisa si la persona ya llegó a su límite diario para esta acción.
    Si no, registra un uso más. Si ya llegó, lanza RuntimeError (el
    router lo convierte en un 429 "demasiadas peticiones").
    """
    limite = LIMITES_POR_DIA.get(accion, 10)
    hoy = date.today().isoformat()
    url, headers = _config_supabase()

    respuesta = requests.get(
        url, headers=headers,
        params={"usuario_id": f"eq.{usuario_id}", "fecha": f"eq.{hoy}", "accion": f"eq.{accion}"},
        timeout=15,
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo verificar el límite de uso: {respuesta.text}")

    filas = respuesta.json()
    contador_actual = filas[0]["contador"] if filas else 0

    if contador_actual >= limite:
        raise RuntimeError(
            f"Llegaste al límite de {limite} usos diarios para esta función. "
            f"Vuelve mañana, o escríbenos a soporte si necesitas más."
        )

    fila = {"usuario_id": usuario_id, "fecha": hoy, "accion": accion, "contador": contador_actual + 1}
    respuesta = requests.post(
        url, headers=headers,
        params={"on_conflict": "usuario_id,fecha,accion"}, json=fila, timeout=15,
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo registrar el uso: {respuesta.text}")
