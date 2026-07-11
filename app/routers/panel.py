import os
import requests
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/panel", tags=["Panel"])


def _config(tabla: str) -> tuple[str, dict]:
    url_base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    clave = os.environ.get("SUPABASE_SERVICE_KEY", "")
    headers = {"apikey": clave, "Authorization": f"Bearer {clave}"}
    return f"{url_base}/rest/v1/{tabla}", headers


def _contar(tabla: str, params: dict | None = None) -> int:
    url, headers = _config(tabla)
    respuesta = requests.get(url, headers=headers, params={**(params or {}), "select": "usuario_id"}, timeout=20)
    if not respuesta.ok:
        return -1
    return len(respuesta.json())


@router.get("/estadisticas")
def estadisticas(clave: str = Query(...)):
    """
    Números simples del negocio: cuántas personas se registraron, cuántas
    tienen premium, referidos canjeados, mensajes de soporte. Protegido
    con una clave secreta — no es para usuarios, solo para ti.
    """
    clave_esperada = os.environ.get("CLAVE_PANEL", "").strip()
    if not clave_esperada or clave != clave_esperada:
        raise HTTPException(status_code=401, detail="Clave incorrecta.")

    return {
        "usuarios_totales": _contar("tokens_acceso"),
        "premium_activos": _contar("suscripciones", {"plan": "eq.premium", "estado": "eq.activa"}),
        "referidos_canjeados": _contar("referidos_canjeados"),
        "resenas_recibidas": _contar("resenas"),
        "nota": "Los ingresos exactos del mes se ven mejor directo en tu Dashboard de Wompi — "
                "aquí solo mostramos actividad de la app.",
    }
