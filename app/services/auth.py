"""
Motor de autenticación — cierre de la Fase 8.

Un sistema simple pero real: cada persona recibe un token secreto único
la primera vez que lo pide. A partir de ahí, cualquier endpoint que
devuelva datos personales (historial, lecturas, estado de pago) exige
ese token — así "conocer el correo de alguien" ya no alcanza para ver
sus datos.

Guardamos solo el HASH del token (nunca el token en sí), igual que se
hace con contraseñas — ni con acceso directo a la base de datos se
podría recuperar el token real de una persona.
"""
import os
import hashlib
import secrets
import requests


def _config_supabase() -> tuple[str, dict]:
    url_base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    clave = os.environ.get("SUPABASE_SERVICE_KEY", "")

    if not url_base or not clave:
        raise RuntimeError(
            "Faltan configurar SUPABASE_URL y SUPABASE_SERVICE_KEY en las variables de entorno."
        )

    headers = {
        "apikey": clave,
        "Authorization": f"Bearer {clave}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    return f"{url_base}/rest/v1/tokens_acceso", headers


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generar_token(usuario_id: str) -> str:
    """
    Genera un token nuevo para una persona (o se lo renueva si ya tenía uno —
    el anterior deja de servir). El token en texto plano solo se devuelve
    esta vez; después solo existe su hash guardado.
    """
    url, headers = _config_supabase()

    token = secrets.token_urlsafe(32)
    fila = {"usuario_id": usuario_id, "token_hash": _hash_token(token)}

    respuesta = requests.post(
        url, headers=headers, params={"on_conflict": "usuario_id"}, json=fila, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo generar el token de acceso: {respuesta.text}")

    return token


def verificar_token(usuario_id: str, token: str | None) -> None:
    """
    Confirma que el token presentado sea el correcto para ese usuario_id.
    Lanza RuntimeError (que el router convierte en un 401) si no lo es.
    """
    if not token:
        raise RuntimeError("Falta el token de acceso (encabezado X-Access-Token).")

    url, headers = _config_supabase()

    respuesta = requests.get(
        url, headers=headers, params={"usuario_id": f"eq.{usuario_id}"}, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo verificar el token: {respuesta.text}")

    filas = respuesta.json()
    if not filas or filas[0]["token_hash"] != _hash_token(token):
        raise RuntimeError("Token de acceso inválido para este usuario_id.")
