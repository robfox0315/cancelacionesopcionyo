# Cancelaciones & Rescates

Dashboard ejecutivo, listo para Angela. 5 pestañas, sin secciones internas de auditoría.

## Datos (actualizados a hoy, 18-ago-2026)
- **Treble**: 2,612 conversaciones (`tag=cancelaciones`), rango abr–ago 2026.
- **HubSpot**: 649 tickets de rescate (categoría "FID- Rescate de reembolsos"), cierre hasta 18-ago-2026 — jalados en vivo vía HubSpot MCP.

## Qué incluye
- Resumen ejecutivo (Treble + HubSpot)
- Carga operativa: mes actual vs. anterior, evolución semanal volumen vs. tiempo
- Funnel operativo (Treble) + funnel financiero (HubSpot)
- Rendimiento por agente (chat + rescate financiero)
- Explorador de casos con descarga CSV

## Pendiente (no bloquea el uso de hoy)
- Conexión en vivo al DWH de Treble vía el Bridge: hoy **caída** (`dwh_conectado: false`, error `Setting max_execution_time is readonly`). No es un problema del dashboard — hay que arreglar la conexión ClickHouse del bridge en Render.
- Llamadas del equipo de cancelaciones: sin acceso confirmado.
- Cruce fila-a-fila Treble↔HubSpot: falta llave `contact_id` común confirmada.

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
