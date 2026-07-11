"""
Motor de soporte — Mejora #11 (la última del roadmap de mejoras).

Un formulario de contacto real dentro de la app, en vez de solo un
enlace "mailto:" que en muchos navegadores de celular no abre nada
(porque no todos tienen una app de correo configurada). Reutiliza
Brevo, que ya está configurado desde la recuperación de cuenta.

El mensaje llega al correo de soporte con "responder a" apuntando al
correo de la persona, así que basta con darle "Responder" al correo
para contestarle directamente — sin tener que copiar nada a mano.
"""
import os
import requests

BREVO_URL = "https://api.brevo.com/v3/smtp/email"
CORREO_SOPORTE = "oraculoastral@outlook.com"


def enviar_mensaje_soporte(usuario_id: str, asunto: str, mensaje: str) -> None:
    """Envía un mensaje de soporte al correo de la marca, vía Brevo (gratis, 300/día)."""
    api_key = os.environ.get("BREVO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Falta configurar BREVO_API_KEY en las variables de entorno del servidor.")

    respuesta = requests.post(
        BREVO_URL,
        headers={"api-key": api_key, "Content-Type": "application/json", "accept": "application/json"},
        json={
            "sender": {"name": "Oráculo Astral — Soporte", "email": CORREO_SOPORTE},
            "to": [{"email": CORREO_SOPORTE}],
            "replyTo": {"email": usuario_id},
            "subject": f"[Soporte Oráculo Astral] {asunto}",
            "htmlContent": f"""
                <div style="font-family:Georgia,serif;color:#222;padding:1.5rem;max-width:560px">
                  <p><strong>De:</strong> {usuario_id}</p>
                  <p><strong>Asunto:</strong> {asunto}</p>
                  <hr style="border:none;border-top:1px solid #ddd;margin:1rem 0">
                  <p style="white-space:pre-line;line-height:1.6">{mensaje}</p>
                </div>
            """,
        },
        timeout=15,
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo enviar el mensaje de soporte: {respuesta.text}")
