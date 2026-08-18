# Cancelaciones & Rescates — Auditoría 360°

## Qué incluye (Fase 1+2, funcional hoy)
- Resumen ejecutivo (Treble + HubSpot)
- Carga operativa: mes actual vs. anterior, evolución semanal volumen vs. tiempo
- Funnel operativo (Treble) + funnel financiero (HubSpot)
- Rendimiento por agente (chat + rescate financiero)
- Cobertura de auditoría (% real, sin inflar — llamadas e IA marcadas en 0%/pendiente)
- Calidad de datos (checks 🟢🟡🔴)
- Explorador de casos con descarga CSV

## Qué queda en segundo plano (a propósito, ver pestaña "Cobertura de auditoría")
- Llamadas del equipo de cancelaciones (sin acceso confirmado — pendiente Diosnel/Alejandro)
- Clasificación por IA de motivo/técnica de rescate (sin acceso al texto de mensajes aún)
- Cruce fila-a-fila Treble↔HubSpot (falta llave contact_id confirmada — hoy son paneles paralelos por fecha)
- Columna "Comisionable" verificada contra Stripe (existe en el dashboard financiero, falta en este export)

## Deploy (mismo patrón que los otros dashboards OY)
1. Repo nuevo en GitHub (ej. `robfox0315/opcionyo-cancelaciones`), branch `main`.
2. Subir `dashboard_cancelaciones_v1.py`, `requirements.txt` y la carpeta `data/` con los dos CSV.
3. Streamlit Cloud → New app → apuntar a `dashboard_cancelaciones_v1.py`.
4. (Opcional) `st.secrets["app_password"]` si quieres la misma pantalla de acceso restringido que los demás dashboards.
5. Para refrescar datos:
   - `data/treble_cancelaciones.csv`: filtro `tag=='cancelaciones'` sobre el export de Treble (`treble_historico.csv` o `treble.csv`).
   - `data/fid_rescate_maestro.csv`: export de HubSpot, categoría "FID- Rescate de reembolsos" (mismo formato que usa `dashboard_reembolsos_disputas.py`).

## Validado antes de entregar
- Sintaxis: OK (`python -m py_compile`)
- Ejecución completa sin excepciones: OK (`streamlit.testing.v1.AppTest`, las 7 pestañas corren sin errores contra los datos reales)
- Datos reales usados en la prueba: 2,179 conversaciones (Treble, tag=cancelaciones, abr–jul 2026) + 587 tickets (HubSpot, categoría FID rescate)

## Lógica de negocio reutilizada (no reinventada)
- RESCATADO / RESCATE EFECTIVO: misma regla de `dashboard_reembolsos_disputas.py` (`Resolución` contiene "rechazado" | "exitoso" | "issue_fixed"). Como este export no trae la columna `Comisionable`, "rescate efectivo" se muestra como aproximación igual al bruto — se marca explícitamente en la UI, no se infla el dato.
- Tiempo de atención: mismo patrón que el tab "Tiempo de Respuesta" de `dashboard_atc_v2.py` (media, mediana, P90 — nunca un solo número suelto).
