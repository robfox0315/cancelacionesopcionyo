"""
╔══════════════════════════════════════════════════════════════╗
║  🎯 CANCELACIONES & RESCATES — AUDITORÍA 360° · OPCIÓN YO     ║
║  Fase 1+2: Resumen ejecutivo, carga operativa, funnel,        ║
║  rendimiento por agente, cobertura y calidad de datos.        ║
║  Fuentes: Treble (tag=cancelaciones) + HubSpot (tickets FID). ║
║  Llamadas / IA: preparadas como próximos pasos (ver footer),  ║
║  no incluidas todavía — sin acceso confirmado.                ║
║  Stack: Streamlit ≥1.40 · Pandas ≥2.1 · Plotly ≥5.20         ║
║  Ejecutar: python -m streamlit run dashboard_cancelaciones_v1.py
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Cancelaciones & Rescates · Opción Yo",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

try:
    IS_DARK = st.context.theme.type == "dark"
except Exception:
    IS_DARK = False

# ── Paleta corporativa (idéntica a los demás dashboards OY) ────
OY_TEAL      = "#16B6C2"
OY_TEAL_DARK = "#0E8E99"
OY_BLUE      = "#2F80ED"
OY_OK        = "#27AE60"
OY_WARN      = "#E5484D"
OY_AMBER     = "#F2A33C"
OY_INK       = "#16323A"
OY_PURPLE    = "#7E57C2"

OY_CHART_TEXT  = "#E8EEF0" if IS_DARK else OY_INK
OY_CHART_TITLE = "#5FD8E3" if IS_DARK else OY_TEAL_DARK

st.markdown("""
<style>
:root{--oy-teal:#16B6C2;--oy-td:#0E8E99;--oy-blue:#2F80ED;
      --oy-ok:#27AE60;--oy-warn:#E5484D;--oy-amb:#F2A33C;--oy-ink:#16323A;}
.block-container{padding-top:1.5rem;}
h1,h2,h3{color:var(--oy-teal);}
[data-testid="stMetricValue"]{font-size:1.7rem!important;font-weight:800;}
[data-testid="stMetricLabel"]{font-size:.78rem!important;font-weight:600;opacity:.85;}

.oy-header{display:flex;align-items:center;gap:18px;
  background:linear-gradient(100deg,var(--oy-td) 0%,var(--oy-teal) 48%,#27D0DC 100%);
  padding:20px 28px;border-radius:16px;margin:2px 0 12px;
  box-shadow:0 8px 22px rgba(22,182,194,.28);overflow:visible;}
.oy-logo{font-weight:800;font-size:2rem;color:#fff;line-height:1.2;
  letter-spacing:.4px;white-space:nowrap;padding:2px 18px 2px 0;
  border-right:2px solid rgba(255,255,255,.4);display:flex;align-items:center;}
.oy-logo span{color:#0A4750;margin-left:6px;}
.oy-htxt{display:flex;flex-direction:column;justify-content:center;}
.oy-htitle{color:#fff;font-weight:800;font-size:1.14rem;margin:0;line-height:1.3;}
.oy-hsub{color:#EAFCFE;font-size:.82rem;margin:3px 0 0;line-height:1.2;}

.sec{background:var(--oy-teal);color:#fff;padding:.4rem 1rem;
  border-radius:8px;font-weight:700;margin:.2rem 0 .7rem;
  font-size:.95rem;display:inline-block;}
.sec.red{background:var(--oy-warn);}
.sec.amb{background:var(--oy-amb);}
.sec.ok{background:var(--oy-ok);}
.sec.blue{background:var(--oy-blue);}
.sec.purple{background:#7E57C2;}
.sec.dark{background:var(--oy-td);}

.kpi-grid{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:8px;}
.kpi{flex:1;min-width:150px;background:var(--oy-teal);border-radius:12px;
  padding:11px 13px;color:#fff;box-shadow:0 4px 12px rgba(22,182,194,.20);}
.kpi.alt{background:var(--oy-blue);}
.kpi.ok{background:var(--oy-ok);}
.kpi.warn{background:var(--oy-warn);}
.kpi.amber{background:var(--oy-amb);}
.kpi.dark{background:var(--oy-td);}
.kpi.purple{background:#7E57C2;}
.kpi .l{font-size:.7rem;opacity:.9;font-weight:600;text-transform:uppercase;letter-spacing:.4px;}
.kpi .v{font-size:1.5rem;font-weight:800;margin-top:2px;}
.kpi .d{font-size:.69rem;opacity:.93;margin-top:2px;}

.crit{background:#FDECEA;border-left:5px solid var(--oy-warn);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#7a1f1c;}
.alrt{background:#FFF6E6;border-left:5px solid var(--oy-amb);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#7a531a;}
.good{background:#EAF7EF;border-left:5px solid var(--oy-ok);
  padding:.6rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#1d6b3a;}
.info{background:#E9F6F8;border-left:5px solid var(--oy-teal);
  padding:.7rem 1rem;border-radius:6px;margin-bottom:.7rem;color:#0E6873;}

.covbar{height:26px;border-radius:6px;background:#E2E8EA;overflow:hidden;
  display:flex;margin:6px 0;}
.covbar .fill{background:var(--oy-teal);height:100%;display:flex;align-items:center;
  justify-content:center;color:#fff;font-weight:700;font-size:.78rem;}

.stTabs [data-baseweb="tab-list"]{gap:3px;flex-wrap:wrap;}
.stTabs [data-baseweb="tab"]{background:#F1FAFB;border-radius:8px 8px 0 0;
  padding:5px 10px;font-weight:600;color:var(--oy-td);}
.stTabs [aria-selected="true"]{background:var(--oy-teal)!important;color:#fff!important;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="oy-header"><div class="oy-logo">opción<span> yo</span></div>'
    '<div class="oy-htxt"><p class="oy-htitle">🎯 Cancelaciones & Rescates — Auditoría 360°</p>'
    '<p class="oy-hsub">Universo de contactos gestionados por el equipo de cancelaciones · '
    'Chats (Treble) + resultado financiero (HubSpot) · Llamadas y clasificación por IA: en preparación, '
    'ver sección de cobertura</p></div></div>',
    unsafe_allow_html=True,
)


# ══════════════════════════════════════════════════════════════
#  AUTENTICACIÓN OPCIONAL (mismo patrón que los demás dashboards OY)
# ══════════════════════════════════════════════════════════════
def _secret(k):
    try:
        return st.secrets.get(k)
    except Exception:
        return None


def require_auth():
    pw = _secret("app_password")
    if not pw or st.session_state.get("auth_ok"):
        return
    st.markdown('<div class="oy-header"><div class="oy-logo">opción<span> yo</span></div>'
                '<div><p class="oy-htitle">Acceso restringido</p>'
                '<p class="oy-hsub">Introduce la contraseña para continuar</p></div></div>',
                unsafe_allow_html=True)
    with st.form("login"):
        inp = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if inp == pw:
                st.session_state["auth_ok"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    st.stop()


require_auth()


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════
def kpi(label, value, delta="", kind=""):
    d = f'<div class="d">{delta}</div>' if delta else ""
    return f'<div class="kpi {kind}"><div class="l">{label}</div><div class="v">{value}</div>{d}</div>'


def sfig(fig, h=340):
    layout_kwargs = dict(
        height=h, margin=dict(t=46, b=10, l=10, r=10),
        font=dict(color=OY_CHART_TEXT, family="Segoe UI,sans-serif"),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color=OY_CHART_TEXT)),
    )
    titulo_actual = fig.layout.title.text if fig.layout.title else None
    if titulo_actual:
        layout_kwargs["title"] = dict(text=titulo_actual, font=dict(color=OY_CHART_TITLE, size=14))
    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(color=OY_CHART_TEXT, gridcolor="rgba(128,128,128,.25)")
    fig.update_yaxes(color=OY_CHART_TEXT, gridcolor="rgba(128,128,128,.25)")
    return fig


def safe_pct(n, d):
    return round(float(n) / float(d) * 100, 1) if d else 0.0


def fmt_usd(v):
    return f"${v:,.2f}"


def fmt_min(v):
    if pd.isna(v):
        return "–"
    if v < 60:
        return f"{v:.1f} min"
    h = int(v // 60)
    m = int(v % 60)
    return f"{h}h {m}min"


def find_data_file(name: str):
    candidates = [
        os.path.join("data", name),
        name,
        os.path.join(os.path.dirname(__file__), "data", name),
        os.path.join(os.path.dirname(__file__), name),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


# ══════════════════════════════════════════════════════════════
#  CARGA Y LIMPIEZA
# ══════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="⏳ Cargando conversaciones de Cancelaciones (Treble)…")
def load_treble_cancelaciones():
    """
    Carga treble_cancelaciones.csv (extracto ya filtrado por tag='cancelaciones')
    si existe. Si no, intenta filtrar treble_historico.csv completo (fallback,
    más lento). Nunca inventa filas — si no hay archivo, avisa y detiene.
    """
    path = find_data_file("treble_cancelaciones.csv")
    if path:
        df = pd.read_csv(path)
    else:
        path_full = find_data_file("treble_historico.csv") or find_data_file("treble.csv")
        if not path_full:
            st.error("❌ No se encontró `data/treble_cancelaciones.csv` ni `treble_historico.csv`. "
                     "Sube el extracto al repositorio.")
            st.stop()
        df_full = pd.read_csv(path_full)
        if "tag" not in df_full.columns:
            st.error("❌ El archivo Treble no tiene columna `tag` — no se puede filtrar por equipo.")
            st.stop()
        df = df_full[df_full["tag"] == "cancelaciones"].copy()

    for c in ["created_at", "finished_at"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", format="mixed")

    df["fecha"] = df["created_at"].dt.date
    df["mes"] = df["created_at"].dt.to_period("M").apply(lambda p: p.start_time.date())
    df["semana"] = df["created_at"].dt.to_period("W").apply(lambda p: p.start_time.date())
    df["hora"] = df["created_at"].dt.hour
    df["dia_nombre"] = df["created_at"].dt.day_name()

    # Tiempo de atención (respuesta): calculado en el DWH (fact_conversations +
    # fact_redirections + fact_agent_messages), no en este script.
    #   - Chats directos: first_response_sec de fact_conversations (asignación → 1er mensaje).
    #   - Chats transferidos desde ATC (CORRECCIÓN reportada por Iva, el mismo problema del
    #     Looker Studio donde el agente que cierra se queda con el tiempo de quien transfirió):
    #     se mide desde la última transferencia hacia Cancelaciones (fact_redirections) hasta
    #     el primer mensaje de un agente DESPUÉS de esa transferencia (fact_agent_messages,
    #     sender='AGENT'), nunca desde la asignación original.
    # "es_transferido" y "tpr_min" ya vienen calculados en el CSV (columnas tpr_min /
    # es_transferido). Se limpian solo valores imposibles como salvaguarda.
    if "tpr_min" not in df.columns:
        df["tpr_min"] = np.nan
    df.loc[(df["tpr_min"] < 0) | (df["tpr_min"] > 7 * 24 * 60), "tpr_min"] = np.nan
    if "es_transferido" not in df.columns:
        df["es_transferido"] = False
    df["es_transferido"] = df["es_transferido"].astype(bool)

    # Duración total del caso (creación -> cierre) — incluye tiempos muertos entre mensajes,
    # es la "carga" total del caso, no el tiempo activo de atención. Se muestran ambas métricas
    # por separado para no mezclar "tiempo de respuesta" con "duración total abierto".
    if "duracion_total_min" not in df.columns:
        df["duracion_total_min"] = (df["finished_at"] - df["created_at"]).dt.total_seconds() / 60
    df.loc[df["duracion_total_min"] < 0, "duracion_total_min"] = np.nan

    df["labels"] = df["labels"].fillna("")
    df["es_cancelar_plan"] = df["labels"].str.contains("Cancelar plan", case=False, na=False)
    df["es_reembolso"] = df["labels"].str.contains("Reembolso", case=False, na=False)
    df["es_intento_cancelacion"] = df["es_cancelar_plan"] | df["es_reembolso"]

    return df


@st.cache_data(show_spinner="⏳ Cargando tickets de rescate (HubSpot)…")
def load_fid_rescate():
    """
    Carga FID_rescate_maestro.csv (export de tickets HubSpot, categoría
    'FID- Rescate de reembolsos'). Reutiliza EXACTAMENTE la regla de negocio
    auditada en dashboard_reembolsos_disputas.py (líneas ~451-457):
      salvado = Resolución contiene "rechazado" | "exitoso" | "issue_fixed"
    """
    path = find_data_file("fid_rescate_maestro.csv") or find_data_file("FID_rescate_maestro.csv")
    if not path:
        st.error("❌ No se encontró `data/fid_rescate_maestro.csv`. Sube el extracto al repositorio.")
        st.stop()
    df = pd.read_csv(path)

    col_agente, col_reso, col_fecha_cierre, col_fecha_creacion, col_monto = (
        "Propietario del ticket", "Resolución", "Fecha de cierre",
        "Fecha de creación", "Monto de reembolso"
    )
    faltan = [c for c in [col_agente, col_reso, col_fecha_cierre] if c not in df.columns]
    if faltan:
        st.error(f"Al CSV de rescates le faltan columnas necesarias: {', '.join(faltan)}.")
        st.stop()

    def _es_salvado(r):
        if pd.isna(r):
            return False
        r = str(r).lower()
        return ("rechazado" in r) or ("exitoso" in r) or ("issue_fixed" in r)

    df["_salvado"] = df[col_reso].apply(_es_salvado)
    df["_cancelacion_confirmada"] = df[col_reso].astype(str).str.contains("aprobado", case=False, na=False)
    df["_fecha_cierre"] = pd.to_datetime(df[col_fecha_cierre], errors="coerce", format="mixed")
    df["_fecha_creacion"] = pd.to_datetime(df[col_fecha_creacion], errors="coerce", format="mixed") if col_fecha_creacion in df.columns else pd.NaT
    df["_mes"] = df["_fecha_cierre"].dt.to_period("M").astype(str)
    df["_agente"] = df[col_agente].fillna("Sin asignar")
    df["_monto"] = pd.to_numeric(df[col_monto], errors="coerce").fillna(0) if col_monto in df.columns else 0.0

    # NOTA DE COBERTURA: este export no trae la columna "Comisionable" (verificación
    # cargo por cargo contra Stripe, sí disponible en dashboard_reembolsos_disputas.py).
    # Mientras no la tengamos aquí, "rescate efectivo" = "rescate bruto" y se marca
    # explícitamente como una aproximación en la UI (no se infla el dato).
    if "Comisionable" in df.columns:
        df["_efectivo"] = df["_salvado"] & df["Comisionable"].astype(str).str.strip().str.lower().isin(
            ["sí", "si", "yes", "true"])
        df["_efectivo_verificado"] = True
    else:
        df["_efectivo"] = df["_salvado"]
        df["_efectivo_verificado"] = False

    if "Tiempo entre la creación y el cierre (HH:mm:ss)" in df.columns:
        def _hhmmss_to_min(v):
            try:
                h, m, s = str(v).split(":")
                return int(h) * 60 + int(m) + int(s) / 60
            except Exception:
                return np.nan
        df["_tiempo_cierre_min"] = df["Tiempo entre la creación y el cierre (HH:mm:ss)"].apply(_hhmmss_to_min)
    else:
        df["_tiempo_cierre_min"] = np.nan

    return df


treble = load_treble_cancelaciones()
fid = load_fid_rescate()

if treble.empty:
    st.warning("No hay conversaciones con tag='cancelaciones' en el archivo cargado.")
    st.stop()

# ══════════════════════════════════════════════════════════════
#  FILTRO GLOBAL DE FECHAS
# ══════════════════════════════════════════════════════════════
min_d, max_d = treble["fecha"].min(), treble["fecha"].max()
c_f1, c_f2 = st.columns([2, 3])
with c_f1:
    rango = st.date_input("📅 Rango de fechas (aplica a Treble y HubSpot)",
                           value=(min_d, max_d), min_value=min_d, max_value=max_d)
if isinstance(rango, tuple) and len(rango) == 2:
    ini, fin = rango
else:
    ini, fin = min_d, max_d

tb = treble[(treble["fecha"] >= ini) & (treble["fecha"] <= fin)].copy()
fb = fid[(fid["_fecha_cierre"].dt.date >= ini) & (fid["_fecha_cierre"].dt.date <= fin)].copy() \
    if fid["_fecha_cierre"].notna().any() else fid.copy()

with c_f2:
    st.caption(
        f"💬 Treble (cancelaciones): {len(tb):,} conversaciones · "
        f"🎫 HubSpot (tickets de rescate): {len(fb):,} tickets cerrados en el rango seleccionado."
    )

# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Resumen Ejecutivo",
    "⏱️ Carga Operativa",
    "🔻 Funnel",
    "🏆 Rendimiento por Agente",
    "📋 Explorador",
])

# ────────────────────────────────────────────────────────────────
# TAB 1 · RESUMEN EJECUTIVO
# ────────────────────────────────────────────────────────────────
with tab1:
    n_intentos = int(tb["es_intento_cancelacion"].sum())
    n_gestionados = int(tb["agent"].notna().sum())
    n_chats_totales = len(tb)

    n_rescatados = int(fb["_salvado"].sum())
    n_efectivos = int(fb["_efectivo"].sum())
    n_gestionados_fid = len(fb)
    n_cancel_confirmadas = int(fb["_cancelacion_confirmada"].sum())
    monto_riesgo = float(fb["_monto"].sum())
    monto_conservado = float(fb.loc[fb["_salvado"], "_monto"].sum())
    monto_perdido = float(fb.loc[fb["_cancelacion_confirmada"], "_monto"].sum())

    tasa_bruta = safe_pct(n_rescatados, n_gestionados_fid)
    tasa_efectiva = safe_pct(n_efectivos, n_gestionados_fid)

    tpr_v = tb["tpr_min"].dropna()
    tpr_prom = tpr_v.mean() if len(tpr_v) else np.nan
    tpr_med = tpr_v.median() if len(tpr_v) else np.nan
    tpr_p90 = tpr_v.quantile(.90) if len(tpr_v) else np.nan
    n_transferidos = int(tb["es_transferido"].sum())

    st.markdown('<div class="sec">📊 KPIs principales — Chats (Treble)</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi("Volumen total de chats", f"{n_chats_totales:,}", "recibidos por el equipo", kind="alt") +
        kpi("Intentos de cancelación", f"{n_intentos:,}", "etiqueta Cancelar plan / Reembolso", kind="warn") +
        kpi("Casos gestionados", f"{n_gestionados:,}", f"{safe_pct(n_gestionados, n_chats_totales)}% con agente", kind="ok") +
        kpi("Tiempo de atención (medio)", fmt_min(tpr_prom), "asignación → 1ᵉʳ mensaje agente", kind="dark") +
        kpi("Mediana", fmt_min(tpr_med), "más robusto a outliers", kind="dark") +
        kpi("P90", fmt_min(tpr_p90), "9 de 10 casos ≤ este valor", kind="dark") +
        '</div>', unsafe_allow_html=True)
    st.caption(
        f"⏱️ Tiempo de atención medido desde el DWH: en chats transferidos desde ATC se mide desde la "
        f"transferencia (no desde la asignación original), corrigiendo el problema reportado por Iva. "
        f"{n_transferidos:,} de {n_chats_totales:,} chats ({safe_pct(n_transferidos, n_chats_totales)}%) "
        f"llegaron transferidos."
    )

    st.markdown('<div class="sec blue">💰 KPIs principales — Resultado financiero (HubSpot / tickets FID)</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="kpi-grid">' +
        kpi("Casos gestionados (FID)", f"{n_gestionados_fid:,}", "tickets cerrados en rango", kind="alt") +
        kpi("Rescatados (bruto)", f"{n_rescatados:,}", f"{tasa_bruta}% tasa bruta", kind="ok") +
        kpi("Rescate efectivo", f"{n_efectivos:,}", f"{tasa_efectiva}% tasa efectiva", kind="ok") +
        kpi("Cancelaciones confirmadas", f"{n_cancel_confirmadas:,}", f"{safe_pct(n_cancel_confirmadas, n_gestionados_fid)}%", kind="warn") +
        kpi("Monto en riesgo", fmt_usd(monto_riesgo), "solicitudes de reembolso", kind="purple") +
        kpi("Monto conservado", fmt_usd(monto_conservado), "no se reembolsó", kind="ok") +
        kpi("Monto perdido", fmt_usd(monto_perdido), "reembolso aprobado", kind="warn") +
        '</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<span class="sec">Volumen de chats por semana</span>', unsafe_allow_html=True)
        vol_sem = tb.groupby("semana").size().reset_index(name="n")
        fig = px.bar(vol_sem, x="semana", y="n", color_discrete_sequence=[OY_TEAL])
        fig.update_layout(xaxis_title="", yaxis_title="Chats")
        st.plotly_chart(sfig(fig, 320), use_container_width=True)
    with col2:
        st.markdown('<span class="sec blue">Resultado de tickets de rescate (HubSpot)</span>', unsafe_allow_html=True)
        reso_counts = fb["Resolución"].value_counts().reset_index()
        reso_counts.columns = ["Resolución", "n"]
        fig = px.pie(reso_counts, names="Resolución", values="n", hole=.5,
                     color_discrete_sequence=[OY_OK, OY_WARN, OY_AMBER, OY_BLUE, "#9CCC65", "#CBD5D9"])
        st.plotly_chart(sfig(fig, 320), use_container_width=True)

    st.markdown('<span class="sec amb">Motivos de solicitud de reembolso (top 10)</span>', unsafe_allow_html=True)
    if "Motivo solicitud de reembolso" in fb.columns:
        mot = fb["Motivo solicitud de reembolso"].value_counts().head(10).reset_index()
        mot.columns = ["Motivo", "n"]
        fig = px.bar(mot, x="n", y="Motivo", orientation="h", color="n",
                     color_continuous_scale=[[0, "#FFF0E0"], [1, OY_AMBER]], text="n")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"}, xaxis_title="Tickets")
        st.plotly_chart(sfig(fig, 380), use_container_width=True)


# ────────────────────────────────────────────────────────────────
# TAB 2 · CARGA OPERATIVA (mes actual vs. mes anterior + semanal)
# ────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec">⏱️ Contexto de carga operativa</div>', unsafe_allow_html=True)
    st.caption("Tiempo de atención corregido: en transferidos se mide desde la transferencia a Cancelaciones.")

    meses_disp = sorted(tb["mes"].dropna().unique(), reverse=True)
    if len(meses_disp) >= 2:
        mes_actual, mes_anterior = meses_disp[0], meses_disp[1]
    elif len(meses_disp) == 1:
        mes_actual, mes_anterior = meses_disp[0], None
    else:
        mes_actual, mes_anterior = None, None

    def _stats_periodo(df_p):
        v = df_p["tpr_min"].dropna()
        return {
            "Volumen (chats)": len(df_p),
            "Tiempo medio": v.mean() if len(v) else np.nan,
            "Mediana": v.median() if len(v) else np.nan,
            "P90": v.quantile(.90) if len(v) else np.nan,
            "Casos por agente": len(df_p) / df_p["agent"].nunique() if df_p["agent"].nunique() else np.nan,
        }

    if mes_actual is not None:
        s_act = _stats_periodo(tb[tb["mes"] == mes_actual])
        s_ant = _stats_periodo(tb[tb["mes"] == mes_anterior]) if mes_anterior else {k: np.nan for k in s_act}

        def _delta_txt(k, fmt=lambda x: f"{x:,.1f}"):
            a, b = s_act[k], s_ant[k]
            if pd.isna(a) or pd.isna(b) or b == 0:
                return "sin comparación"
            pct = (a - b) / b * 100
            flecha = "🔺" if pct > 0 else "🔻"
            return f"{flecha} {pct:+.0f}% vs. mes anterior ({fmt(b)})"

        st.markdown(f"<b>Comparación: {mes_actual.strftime('%b %Y')} vs. "
                     f"{mes_anterior.strftime('%b %Y') if mes_anterior else '(sin mes anterior en el rango)'}</b>",
                     unsafe_allow_html=True)
        st.markdown('<div class="kpi-grid">' +
            kpi("Volumen", f"{s_act['Volumen (chats)']:,}", _delta_txt("Volumen (chats)", lambda x: f"{x:,.0f}"), kind="alt") +
            kpi("Tiempo medio", fmt_min(s_act["Tiempo medio"]), _delta_txt("Tiempo medio", fmt_min), kind="dark") +
            kpi("Mediana", fmt_min(s_act["Mediana"]), _delta_txt("Mediana", fmt_min), kind="dark") +
            kpi("P90", fmt_min(s_act["P90"]), _delta_txt("P90", fmt_min), kind="dark") +
            kpi("Casos por agente", f"{s_act['Casos por agente']:.1f}", _delta_txt("Casos por agente", lambda x: f"{x:.1f}"), kind="purple") +
            '</div>', unsafe_allow_html=True)

        # Lectura automática (no interpretación forzada — solo compara las dos variables)
        d_vol = s_act["Volumen (chats)"] - s_ant["Volumen (chats)"] if not pd.isna(s_ant["Volumen (chats)"]) else None
        d_tpr = s_act["Tiempo medio"] - s_ant["Tiempo medio"] if not pd.isna(s_ant["Tiempo medio"]) else None
        if d_vol is not None and d_tpr is not None and s_ant["Volumen (chats)"] and s_ant["Tiempo medio"]:
            pct_vol = d_vol / s_ant["Volumen (chats)"] * 100
            pct_tpr = d_tpr / s_ant["Tiempo medio"] * 100
            if pct_tpr > 15 and pct_vol < pct_tpr - 15:
                st.markdown(f'<div class="crit">⚠️ El tiempo de atención subió {pct_tpr:+.0f}% mientras el '
                             f'volumen cambió {pct_vol:+.0f}% — el aumento de tiempo <b>no se explica solo por '
                             f'más volumen</b>. Vale la pena revisar carga por agente o posible cuello de botella '
                             f'operativo.</div>', unsafe_allow_html=True)
            elif pct_tpr > 15 and pct_vol >= pct_tpr - 15:
                st.markdown(f'<div class="alrt">📈 El tiempo subió {pct_tpr:+.0f}% y el volumen también subió '
                             f'{pct_vol:+.0f}% — parte del aumento de tiempo es consistente con mayor carga, '
                             f'no necesariamente ineficiencia.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="good">✅ El tiempo de atención se mantiene relativamente estable '
                             'entre ambos meses.</div>', unsafe_allow_html=True)
    else:
        st.info("No hay suficientes meses en el rango seleccionado para comparar.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec blue">Evolución semanal: volumen vs. tiempo de atención</span>',
                unsafe_allow_html=True)
    eg = tb.groupby("semana").agg(
        volumen=("phone", "size"),
        tpr_medio=("tpr_min", "mean"),
        tpr_p90=("tpr_min", lambda x: x.quantile(.90)),
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=eg["semana"], y=eg["volumen"], name="Volumen (chats)",
                          marker_color=OY_TEAL, yaxis="y1", opacity=.55))
    fig.add_trace(go.Scatter(x=eg["semana"], y=eg["tpr_medio"], name="Tiempo medio (min)",
                              mode="lines+markers", line=dict(color=OY_WARN, width=3), yaxis="y2"))
    fig.add_trace(go.Scatter(x=eg["semana"], y=eg["tpr_p90"], name="P90 (min)",
                              mode="lines+markers", line=dict(color=OY_AMBER, width=2, dash="dot"), yaxis="y2"))
    fig.update_layout(
        yaxis=dict(title="Chats"), yaxis2=dict(title="Minutos", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.15))
    st.plotly_chart(sfig(fig, 380), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<span class="sec">Casos por agente (rango actual)</span>', unsafe_allow_html=True)
        cxa = tb.groupby("agent").size().reset_index(name="n").sort_values("n", ascending=False)
        fig = px.bar(cxa, x="n", y="agent", orientation="h", color="n",
                     color_continuous_scale=[[0, "#E9F6F8"], [1, OY_TEAL]], text="n")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, yaxis={"categoryorder": "total ascending"}, xaxis_title="Chats")
        st.plotly_chart(sfig(fig, 320), use_container_width=True)
    with c2:
        st.markdown('<span class="sec">Casos por hora del día</span>', unsafe_allow_html=True)
        cxh = tb.groupby("hora").size().reset_index(name="n")
        fig = px.bar(cxh, x="hora", y="n", color_discrete_sequence=[OY_BLUE])
        fig.update_layout(xaxis_title="Hora", yaxis_title="Chats")
        st.plotly_chart(sfig(fig, 320), use_container_width=True)


# ────────────────────────────────────────────────────────────────
# TAB 3 · FUNNEL
# ────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec">🔻 Funnel de cancelación</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<span class="sec dark">Funnel operativo (Treble)</span>', unsafe_allow_html=True)
        etapas_op = ["Contactado por Cancelaciones", "Gestionado (con agente)", "Intención explícita de cancelar"]
        valores_op = [len(tb), int(tb["agent"].notna().sum()), int(tb["es_intento_cancelacion"].sum())]
        fig = go.Figure(go.Funnel(
            y=etapas_op, x=valores_op,
            textinfo="value+percent initial",
            marker=dict(color=[OY_TEAL, OY_TEAL_DARK, OY_BLUE])))
        st.plotly_chart(sfig(fig, 340), use_container_width=True)

    with c2:
        st.markdown('<span class="sec blue">Funnel financiero (HubSpot / FID rescate)</span>', unsafe_allow_html=True)
        etapas_fin = ["Ticket de rescate gestionado", "Rescatado (bruto)", "Rescate efectivo", "Cancelación confirmada"]
        valores_fin = [len(fb), int(fb["_salvado"].sum()), int(fb["_efectivo"].sum()), int(fb["_cancelacion_confirmada"].sum())]
        fig = go.Figure(go.Funnel(
            y=etapas_fin, x=valores_fin,
            textinfo="value+percent initial",
            marker=dict(color=[OY_BLUE, OY_OK, OY_TEAL_DARK, OY_WARN])))
        st.plotly_chart(sfig(fig, 340), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec amb">Caída entre etapas (funnel financiero)</span>', unsafe_allow_html=True)
    caidas = []
    for i in range(1, len(valores_fin)):
        prev, cur = valores_fin[i-1], valores_fin[i]
        caidas.append({
            "Etapa": f"{etapas_fin[i-1]} → {etapas_fin[i]}",
            "De": prev, "A": cur,
            "Conversión %": safe_pct(cur, prev),
            "Caída": prev - cur,
        })
    st.dataframe(pd.DataFrame(caidas), use_container_width=True, hide_index=True)


# ────────────────────────────────────────────────────────────────
# TAB 4 · RENDIMIENTO POR AGENTE
# ────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec">🏆 Rendimiento por agente — operativo + financiero</div>', unsafe_allow_html=True)
    st.caption("🔸 = muestra pequeña (menos de 15 casos en el rango seleccionado). "
               "Tiempo de atención incluye chats transferidos, medido desde la transferencia.")

    op_ag = tb.groupby("agent").agg(
        Casos_chat=("phone", "size"),
        Casos_transferidos=("es_transferido", "sum"),
        Tiempo_medio=("tpr_min", "mean"),
        Tiempo_mediana=("tpr_min", "median"),
        Tiempo_P90=("tpr_min", lambda x: x.quantile(.90)),
    ).reset_index().rename(columns={"agent": "Agente"})

    fin_ag = fb.groupby("_agente").agg(
        Casos_ticket=("_agente", "size"),
        Salvados=("_salvado", "sum"),
        Efectivos=("_efectivo", "sum"),
        Cancel_confirmadas=("_cancelacion_confirmada", "sum"),
        Monto_gestionado=("_monto", "sum"),
        Monto_conservado=("_monto", lambda x: x[fb.loc[x.index, "_salvado"]].sum()),
    ).reset_index().rename(columns={"_agente": "Agente"})
    fin_ag["Tasa bruta %"] = (fin_ag["Salvados"] / fin_ag["Casos_ticket"] * 100).round(1)
    fin_ag["Tasa efectiva %"] = (fin_ag["Efectivos"] / fin_ag["Casos_ticket"] * 100).round(1)
    fin_ag["Muestra"] = fin_ag["Casos_ticket"].apply(lambda n: "🔸 pequeña" if n < 15 else "")

    tabla = fin_ag.merge(op_ag, on="Agente", how="outer")
    tabla = tabla.sort_values("Casos_ticket", ascending=False, na_position="last")

    st.markdown('<span class="sec blue">Resultado financiero por agente (HubSpot)</span>', unsafe_allow_html=True)
    cols_fin = ["Agente", "Casos_ticket", "Salvados", "Efectivos", "Tasa bruta %", "Tasa efectiva %",
                "Cancel_confirmadas", "Monto_gestionado", "Monto_conservado", "Muestra"]
    disp = tabla[[c for c in cols_fin if c in tabla.columns]].copy()
    for c in ["Monto_gestionado", "Monto_conservado"]:
        if c in disp.columns:
            disp[c] = disp[c].apply(lambda v: fmt_usd(v) if pd.notna(v) else "–")
    st.dataframe(disp, use_container_width=True, hide_index=True, height=340)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec dark">Carga operativa por agente (Treble)</span>', unsafe_allow_html=True)
    cols_op = ["Agente", "Casos_chat", "Casos_transferidos", "Tiempo_medio", "Tiempo_mediana", "Tiempo_P90"]
    disp_op = tabla[[c for c in cols_op if c in tabla.columns]].copy()
    disp_op["% Transferidos"] = (disp_op["Casos_transferidos"] / disp_op["Casos_chat"] * 100).round(1)
    for c in ["Tiempo_medio", "Tiempo_mediana", "Tiempo_P90"]:
        if c in disp_op.columns:
            disp_op[c] = disp_op[c].apply(fmt_min)
    st.dataframe(disp_op, use_container_width=True, hide_index=True, height=340)

    c1, c2 = st.columns(2)
    with c1:
        plot_df = fin_ag[fin_ag["Casos_ticket"] >= 5].sort_values("Tasa efectiva %", ascending=True)
        fig = px.bar(plot_df, x="Tasa efectiva %", y="Agente", orientation="h",
                     color="Tasa efectiva %", color_continuous_scale="RdYlGn", text="Casos_ticket",
                     title="Tasa de rescate efectivo por agente (≥5 casos)")
        fig.update_traces(texttemplate="n=%{text}", textposition="outside")
        st.plotly_chart(sfig(fig, 340), use_container_width=True)
    with c2:
        st.markdown('<span class="sec dark">Tiempo de atención por agente (Treble)</span>', unsafe_allow_html=True)
        op_plot = op_ag.dropna(subset=["Tiempo_medio"]).sort_values("Tiempo_medio")
        fig = px.bar(op_plot, x="Tiempo_medio", y="Agente", orientation="h",
                     color="Tiempo_medio", color_continuous_scale="RdYlGn_r",
                     labels={"Tiempo_medio": "min"}, title="Tiempo medio de respuesta (min)")
        st.plotly_chart(sfig(fig, 340), use_container_width=True)


# ────────────────────────────────────────────────────────────────
# TAB 5 · EXPLORADOR
# ────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="sec">📋 Explorador de casos</div>', unsafe_allow_html=True)
    fuente = st.radio("Fuente", ["Chats (Treble)", "Tickets de rescate (HubSpot)"], horizontal=True)

    if fuente == "Chats (Treble)":
        agentes = sorted(tb["agent"].dropna().unique())
        f_agente = st.multiselect("Agente", agentes)
        buscar = st.text_input("Buscar por teléfono o contacto")
        d = tb.copy()
        if f_agente:
            d = d[d["agent"].isin(f_agente)]
        if buscar:
            d = d[d["phone"].astype(str).str.contains(buscar, na=False) |
                  d["contact"].astype(str).str.contains(buscar, case=False, na=False)]
        cols = ["phone", "contact", "agent", "created_at", "finished_at", "tpr_min",
                "duracion_total_min", "labels", "rating", "status"]
        st.dataframe(d[[c for c in cols if c in d.columns]], use_container_width=True, hide_index=True, height=460)
        st.download_button("⬇️ CSV filtrado", d.to_csv(index=False).encode(), "cancelaciones_chats.csv", "text/csv")
    else:
        agentes_f = sorted(fb["_agente"].dropna().unique())
        f_agente = st.multiselect("Agente", agentes_f)
        d = fb.copy()
        if f_agente:
            d = d[d["_agente"].isin(f_agente)]
        cols = ["Ticket ID", "Propietario del ticket", "Resolución", "Motivo solicitud de reembolso",
                "Fecha de creación", "Fecha de cierre", "Monto de reembolso", "Reembolsado en Stripe"]
        st.dataframe(d[[c for c in cols if c in d.columns]], use_container_width=True, hide_index=True, height=460)
        st.download_button("⬇️ CSV filtrado", d.to_csv(index=False).encode(), "cancelaciones_tickets.csv", "text/csv")


st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Dashboard Cancelaciones & Rescates · Opción Yo — actualizado a hoy.")
