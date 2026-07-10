# Oráculo Astral — Backend

API del Proyecto 09 · sistema de guía espiritual diaria.

## Stack

- **Python + FastAPI** — API principal
- **Swiss Ephemeris (pyswisseph)** — cálculo astronómico real de cartas natales
- Próximamente: Claude (motor de lectura), ElevenLabs (audio), Stripe/Wompi (pagos)

## Estructura

```
backend/
  app/
    main.py              # punto de entrada FastAPI
    routers/
      carta_natal.py      # endpoints HTTP
    services/
      carta_natal.py      # lógica de cálculo con Swiss Ephemeris
    models/               # (próximo) modelos de base de datos
  requirements.txt
```

## Correr localmente

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda en `http://localhost:8000`, con documentación interactiva automática en `http://localhost:8000/docs`.

## Endpoints (Fase 1)

- `GET /salud` — chequeo de estado
- `POST /carta-natal/calcular` — calcula una carta natal real a partir de fecha, hora y coordenadas de nacimiento

### Ejemplo de request

```json
{
  "fecha": "1995-03-21",
  "hora": "14:30",
  "lat": 6.2442,
  "lon": -75.5812,
  "zona_horaria_utc_offset": -5
}
```

## Fase actual: 1 · Fundamentos técnicos ✅

*(Proyecto renombrado de "Oráculo IA" a "Oráculo Astral" — mismo backend, mismo motor.)*

- [x] Estructura del proyecto
- [x] Swiss Ephemeris integrado y probado con datos reales
- [x] Primer endpoint funcionando end-to-end

## Siguiente: Fase 2 · Carta natal real

Expandir el motor: geocodificación de lugares de nacimiento (convertir "Medellín, Colombia" en lat/lon automáticamente), manejo de zonas horarias históricas, y aspectos planetarios (conjunciones, oposiciones, trígonos).
