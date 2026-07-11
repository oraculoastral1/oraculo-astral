"""
Correos automáticos — bienvenida al registrarse, y recordatorio diario
para que el ritual de la lectura matutina no se olvide. Ambos usan
Brevo, ya configurado desde la recuperación de cuenta.
"""
import os
import requests

BREVO_URL = "https://api.brevo.com/v3/smtp/email"
REMITENTE = {"name": "Oráculo Astral", "email": "oraculoastral@outlook.com"}
URL_APP = "https://oraculoastral1.github.io/oraculo-astral/app.html"


def _enviar(destinatario: str, asunto: str, html: str) -> None:
    api_key = os.environ.get("BREVO_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Falta configurar BREVO_API_KEY en las variables de entorno del servidor.")

    respuesta = requests.post(
        BREVO_URL,
        headers={"api-key": api_key, "Content-Type": "application/json", "accept": "application/json"},
        json={"sender": REMITENTE, "to": [{"email": destinatario}], "subject": asunto, "htmlContent": html},
        timeout=15,
    )
    if not respuesta.ok:
        raise RuntimeError(f"No se pudo enviar el correo: {respuesta.text}")


def enviar_correo_bienvenida(usuario_id: str, nombre: str) -> None:
    saludo = f"Hola{', ' + nombre if nombre else ''}"
    html = f"""
    <div style="background:#070510;color:#cfc8e2;font-family:Georgia,serif;padding:2.5rem;text-align:center">
      <h1 style="color:#f5efe2;font-size:1.5rem">Oráculo <span style="color:#d4af6a;font-style:italic">Astral</span></h1>
      <p style="margin-top:1.5rem;font-size:1rem">{saludo}, bienvenida a tu nuevo ritual diario ✦</p>
      <p style="font-size:.92rem;color:#b9b3cc;max-width:420px;margin:1rem auto">
        Cada mañana, tu carta natal real se convierte en una guía escrita solo para ti.
        Vuelve cuando quieras, tu cielo te está esperando.
      </p>
      <a href="{URL_APP}" style="display:inline-block;margin-top:1.2rem;background:#d4af6a;color:#14101f;
        padding:.8rem 1.8rem;border-radius:4px;text-decoration:none;font-family:sans-serif;font-size:.85rem;font-weight:600">
        Ver mi lectura de hoy
      </a>
    </div>
    """
    _enviar(usuario_id, "Bienvenida a Oráculo Astral ✦", html)


def enviar_recordatorio_diario(usuario_id: str, nombre: str) -> None:
    saludo = nombre if nombre else "viajera"
    html = f"""
    <div style="background:#070510;color:#cfc8e2;font-family:Georgia,serif;padding:2.5rem;text-align:center">
      <h1 style="color:#f5efe2;font-size:1.3rem">Oráculo <span style="color:#d4af6a;font-style:italic">Astral</span></h1>
      <p style="margin-top:1.5rem;font-size:1.1rem;font-style:italic;color:#f0dca8">Tu cielo tiene algo que decirte hoy, {saludo}.</p>
      <a href="{URL_APP}" style="display:inline-block;margin-top:1.4rem;background:#d4af6a;color:#14101f;
        padding:.8rem 1.8rem;border-radius:4px;text-decoration:none;font-family:sans-serif;font-size:.85rem;font-weight:600">
        Ver mi lectura de hoy
      </a>
    </div>
    """
    _enviar(usuario_id, "Tu lectura de hoy te está esperando ✦", html)
