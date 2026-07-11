"""
Motor del programa de referidos — Mejora #9.

Cada persona tiene un código único para invitar a otras. Cuando alguien
nuevo se registra usando ese código, ambas ganan días de premium gratis
— quien invitó y quien fue invitada.

Reglas anti-abuso simples pero honestas para esta etapa (pocos usuarios):
- Cada persona solo puede CANJEAR un código una vez en la vida (no puede
  usar varios códigos para acumular recompensas infinitas).
- Nadie puede canjear su propio código.
Nota: esto es suficiente para una comunidad pequeña de confianza; si el
proyecto crece mucho, valdría la pena verificar también que la cuenta
invitada sea genuinamente nueva (no solo un correo distinto de la misma persona).
"""
import os
import re
import secrets
import requests

from app.services.suscripciones import agregar_dias_premium

DIAS_RECOMPENSA = 7


def _config_supabase(tabla: str) -> tuple[str, dict]:
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
    return f"{url_base}/rest/v1/{tabla}", headers


def _generar_codigo_base(usuario_id: str) -> str:
    """Arma un código legible a partir del correo (ej: ana@x.com -> ANA4K92)."""
    base = re.sub(r"[^a-zA-Z]", "", usuario_id.split("@")[0]).upper()[:6] or "ORACULO"
    sufijo = secrets.token_hex(2).upper()
    return f"{base}{sufijo}"


def obtener_o_crear_codigo(usuario_id: str) -> str:
    """Devuelve el código de referido de la persona, generándolo si es su primera vez."""
    url, headers = _config_supabase("codigos_referido")

    respuesta = requests.get(url, headers=headers, params={"usuario_id": f"eq.{usuario_id}"}, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo consultar el código de referido: {respuesta.text}")

    filas = respuesta.json()
    if filas:
        return filas[0]["codigo"]

    codigo = _generar_codigo_base(usuario_id)
    fila = {"usuario_id": usuario_id, "codigo": codigo}
    respuesta = requests.post(url, headers=headers, params={"on_conflict": "usuario_id"}, json=fila, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo generar el código de referido: {respuesta.text}")

    return codigo


def _buscar_dueno_codigo(codigo: str) -> str | None:
    url, headers = _config_supabase("codigos_referido")
    respuesta = requests.get(url, headers=headers, params={"codigo": f"eq.{codigo.upper()}"}, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo verificar el código: {respuesta.text}")
    filas = respuesta.json()
    return filas[0]["usuario_id"] if filas else None


def _ya_canjeo(usuario_id: str) -> bool:
    url, headers = _config_supabase("referidos_canjeados")
    respuesta = requests.get(url, headers=headers, params={"usuario_id": f"eq.{usuario_id}"}, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo verificar el canje: {respuesta.text}")
    return bool(respuesta.json())


def canjear_codigo(usuario_id_nuevo: str, codigo: str) -> dict:
    """
    Valida y aplica el canje de un código de invitación. Da DIAS_RECOMPENSA
    días de premium tanto a quien invitó como a quien se unió.
    """
    codigo = codigo.strip().upper()
    dueno = _buscar_dueno_codigo(codigo)
    if not dueno:
        raise RuntimeError("Ese código de invitación no existe.")
    if dueno == usuario_id_nuevo:
        raise RuntimeError("No puedes usar tu propio código de invitación.")
    if _ya_canjeo(usuario_id_nuevo):
        raise RuntimeError("Ya usaste un código de invitación antes — solo se puede una vez por cuenta.")

    agregar_dias_premium(usuario_id_nuevo, DIAS_RECOMPENSA, proveedor="referido")
    agregar_dias_premium(dueno, DIAS_RECOMPENSA, proveedor="referido")

    url, headers = _config_supabase("referidos_canjeados")
    fila = {"usuario_id": usuario_id_nuevo, "codigo": codigo, "referente_usuario_id": dueno}
    respuesta = requests.post(url, headers=headers, params={"on_conflict": "usuario_id"}, json=fila, timeout=15)
    if not respuesta.ok:
        raise RuntimeError(f"El canje se aplicó pero no se pudo registrar: {respuesta.text}")

    return {"dias_otorgados": DIAS_RECOMPENSA}
