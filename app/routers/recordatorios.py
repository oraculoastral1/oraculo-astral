from datetime import date
from fastapi import APIRouter, HTTPException, Query

from app.services.perfiles import listar_perfiles_para_recordatorio, marcar_recordatorio_enviado
from app.services.correos import enviar_recordatorio_diario
import os

router = APIRouter(prefix="/recordatorios", tags=["Recordatorios"])


@router.get("/enviar-diarios")
def enviar_diarios(clave: str = Query(...)):
    """
    Envía el recordatorio diario a todas las personas con perfil guardado.
    Pensado para ser llamado UNA VEZ AL DÍA por un servicio externo gratis
    de cron (ej: cron-job.org), nunca manualmente por una persona — por
    eso exige una clave secreta en vez de un token de usuario.
    """
    clave_esperada = os.environ.get("CLAVE_RECORDATORIOS", "").strip()
    if not clave_esperada or clave != clave_esperada:
        raise HTTPException(status_code=401, detail="Clave incorrecta.")

    try:
        perfiles = listar_perfiles_para_recordatorio()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    hoy = date.today().isoformat()
    enviados, fallidos = 0, 0
    for perfil in perfiles:
        if perfil.get("ultimo_recordatorio_enviado") == hoy:
            continue  # ya se le mandó hoy (evita duplicados si el cron se dispara más de una vez)
        try:
            enviar_recordatorio_diario(perfil["usuario_id"], perfil.get("nombre") or "")
            marcar_recordatorio_enviado(perfil["usuario_id"], hoy)
            enviados += 1
        except RuntimeError:
            fallidos += 1

    return {"enviados": enviados, "fallidos": fallidos, "total_perfiles": len(perfiles)}
