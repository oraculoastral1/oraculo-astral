"""
Motor de perfiles — guarda una copia mínima de los datos de cada persona
(nombre, nacimiento) del lado del servidor, para poder mandarle el
recordatorio diario por correo sin depender de que su navegador
todavía tenga la sesión guardada.
"""
import os
import requests


def _config_supabase() -> tuple[str, dict]:
    url_base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    clave = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url_base or not clave:
        raise RuntimeError("Faltan configurar SUPABASE_URL y SUPABASE_SERVICE_KEY en las variables de entorno.")
    headers = {
        "apikey": clave, "Authorization": f"Bearer {clave}",
        "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates",
    }
    return f"{url_base}/rest/v1/perfiles", headers


def guardar_perfil(usuario_id: str, nombre: str, fecha_nacimiento: str, hora_nacimiento: str, ciudad: str) -> None:
    """Guarda o actualiza el perfil de la persona (best-effort, no debe romper el flujo principal)."""
    url, headers = _config_supabase()
    fila = {
        "usuario_id": usuario_id,
        "nombre": nombre or None,
        "fecha_nacimiento": fecha_nacimiento,
        "hora_nacimiento": hora_nacimiento,
        "ciudad": ciudad,
    }
    respuesta = requests.post(url, headers=headers, params={"on_conflict": "usuario_id"}, json=fila, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo guardar el perfil: {respuesta.text}")


def listar_perfiles_para_recordatorio() -> list[dict]:
    """Trae todos los perfiles guardados, para el envío del recordatorio diario."""
    url, headers = _config_supabase()
    respuesta = requests.get(url, headers=headers, params={"select": "*"}, timeout=20)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo listar los perfiles: {respuesta.text}")
    return respuesta.json()


def marcar_recordatorio_enviado(usuario_id: str, fecha_iso: str) -> None:
    url, headers = _config_supabase()
    requests.patch(
        url, headers=headers, params={"usuario_id": f"eq.{usuario_id}"},
        json={"ultimo_recordatorio_enviado": fecha_iso}, timeout=15,
    )
