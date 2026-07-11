"""
Motor de recuperación de cuenta — Mejora #3.

Antes de esto, cualquiera que supiera el correo de una persona podía
generar un token nuevo para su cuenta sin ninguna verificación —
una puerta trasera real. Ahora, recuperar el acceso exige demostrar
que se es dueño del correo: se manda un código de 6 dígitos por
email (vía Brevo, gratis), y solo con ese código se emite un token
nuevo.

Igual que con los tokens de acceso, guardamos solo el HASH del código,
nunca el código en texto plano. Cada código expira a los 10 minutos y
se invalida apenas se usa una vez.
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import requests

BREVO_URL = "https://api.brevo.com/v3/smtp/email"
MINUTOS_VALIDEZ = 10


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
    return f"{url_base}/rest/v1/codigos_verificacion", headers


def _hash_codigo(codigo: str) -> str:
    return hashlib.sha256(codigo.encode("utf-8")).hexdigest()


def _enviar_email_codigo(destinatario: str, codigo: str) -> None:
    """Envía el código de verificación por correo usando Brevo (gratis, 300/día)."""
    api_key = os.environ.get("BREVO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Falta configurar BREVO_API_KEY en las variables de entorno del servidor.")

    respuesta = requests.post(
        BREVO_URL,
        headers={"api-key": api_key, "Content-Type": "application/json", "accept": "application/json"},
        json={
            "sender": {"name": "Oráculo Astral", "email": "oraculoastral@outlook.com"},
            "to": [{"email": destinatario}],
            "subject": "Tu código para recuperar tu acceso — Oráculo Astral",
            "htmlContent": f"""
                <div style="background:#070510;color:#cfc8e2;font-family:Georgia,serif;padding:2.5rem;text-align:center">
                  <h1 style="color:#f5efe2;font-size:1.4rem">Oráculo <span style="color:#d4af6a;font-style:italic">Astral</span></h1>
                  <p style="margin-top:1.5rem;font-size:.95rem">Tu código para recuperar el acceso a tu cuenta es:</p>
                  <div style="font-size:2.2rem;letter-spacing:.3em;color:#f0dca8;font-weight:bold;margin:1.2rem 0">{codigo}</div>
                  <p style="font-size:.82rem;color:#8b84a3">Válido por {MINUTOS_VALIDEZ} minutos. Si no lo pediste tú, ignora este correo.</p>
                </div>
            """,
        },
        timeout=15,
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo enviar el correo de verificación: {respuesta.text}")


def generar_y_enviar_codigo(usuario_id: str) -> None:
    """Genera un código de 6 dígitos, lo guarda (hasheado) y lo manda por email."""
    url, headers = _config_supabase()

    codigo = f"{secrets.randbelow(1_000_000):06d}"
    expira_en = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_VALIDEZ)

    fila = {
        "usuario_id": usuario_id,
        "codigo_hash": _hash_codigo(codigo),
        "expira_en": expira_en.isoformat(),
    }
    respuesta = requests.post(
        url, headers=headers, params={"on_conflict": "usuario_id"}, json=fila, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo generar el código de recuperación: {respuesta.text}")

    _enviar_email_codigo(usuario_id, codigo)


def verificar_codigo(usuario_id: str, codigo: str) -> None:
    """
    Confirma que el código sea correcto y no haya expirado.
    Lanza RuntimeError si es inválido — el router lo convierte en un 401.
    """
    url, headers = _config_supabase()

    respuesta = requests.get(
        url, headers=headers, params={"usuario_id": f"eq.{usuario_id}"}, timeout=15
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo verificar el código: {respuesta.text}")

    filas = respuesta.json()
    if not filas:
        raise RuntimeError("No hay ningún código pendiente para este correo. Solicita uno nuevo.")

    fila = filas[0]
    expira_en = datetime.fromisoformat(fila["expira_en"])
    if expira_en < datetime.now(timezone.utc):
        raise RuntimeError("Este código ya expiró. Solicita uno nuevo.")

    if fila["codigo_hash"] != _hash_codigo(codigo):
        raise RuntimeError("El código no es correcto.")

    # Se invalida apenas se usa, para que no se pueda reutilizar
    requests.delete(url, headers=headers, params={"usuario_id": f"eq.{usuario_id}"}, timeout=15)
