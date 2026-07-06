"""Tema visual corporativo Sapiencia.

Define la paleta de colores oficial y una función `inject_global_css()`
que inyecta los estilos globales en la app de Streamlit.

Llamar `inject_global_css()` una sola vez al inicio de `main.py`.

Regla general de contraste (CORRECCIÓN V2):
- Sobre fondo BLANCO  → texto `#AB2181` o `#7D1860` o `#3D3D3D`.
- Sobre fondo MAGENTA → texto `#FFFFFF` SIEMPRE.
- Nunca texto `#AB2181` sobre fondo `#AB2181`.
"""
from __future__ import annotations

from typing import Dict

# ---------------------------------------------------------------------------
# Paleta corporativa Sapiencia
# ---------------------------------------------------------------------------
SAPIENCIA_COLORS: Dict[str, str] = {
    "magenta_primary": "#AB2181",   # Color principal
    "magenta_light": "#C9549A",
    "magenta_dark": "#7D1860",
    "gray_dark": "#3D3D3D",
    "gray_medium": "#6B6B6B",
    "gray_light": "#F5F5F5",
    "white": "#FFFFFF",
    "success_green": "#2E7D32",
    "warning_amber": "#F57F17",
    "error_red": "#C62828",
}


# ---------------------------------------------------------------------------
# CSS global (CORRECCIÓN V2: reglas estrictas de contraste)
# ---------------------------------------------------------------------------
_GLOBAL_CSS_TEMPLATE = """
<style>
/* ============================================================
   CORRECCIÓN V4.1: preservar fuente Material Icons / Symbols
   El control de expandir/colapsar el sidebar (y otros controles
   internos de Streamlit) renderizan glifos via ligaduras de las
   fuentes "Material Icons" / "Material Symbols *". Si el CSS
   global les fuerza Calibri, el navegador muestra el texto
   literal de la ligadura (p.ej. "keyboard_double_arrow_right").
   Estas reglas deben ir ANTES de la regla genérica de fuente y
   usar `!important` para sobrevivir a cualquier otra cascada.
   ============================================================ */
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] *,
[data-testid="baseButton-headerNoPadding"],
[data-testid="baseButton-headerNoPadding"] *,
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] *,
.material-icons,
.material-icons-outlined,
.material-icons-rounded,
[class*="material-icon"],
[class*="material-symbol"],
[class*="MaterialSymbols"] {{
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                 'Material Icons', 'Material Icons Rounded',
                 'Material Icons Outlined' !important;
    font-style: normal !important;
    font-weight: normal !important;
    font-variant: normal !important;
    text-transform: none !important;
    letter-spacing: normal !important;
    word-wrap: normal !important;
    line-height: 1 !important;
    -webkit-font-feature-settings: 'liga' !important;
    -webkit-font-smoothing: antialiased !important;
}}

/* ── Fuente base (selectores acotados — NO afecta íconos) ──
   Quitar `[class*="css"]`, `span`, `div` que golpeaban ligaduras
   de Material Icons en controles internos de Streamlit. */
html, body,
.main .block-container,
section[data-testid="stSidebar"] .block-container,
.stApp, .stMarkdown, .stTextInput, .stSelectbox,
.stButton, .stMetric,
h1, h2, h3, h4, h5, h6, p {{
    font-family: 'Calibri', 'Arial', sans-serif !important;
}}

/* ── Headers de sección: magenta sobre fondo blanco ── */
.main h1, .main h2, .main h3,
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3 {{
    color: {magenta_primary} !important;
    font-weight: 700;
}}

/* ── Sidebar: fondo magenta oscuro, texto siempre blanco ── */
section[data-testid="stSidebar"] {{
    background-color: {magenta_dark} !important;
}}
/* Texto blanco para el contenido del sidebar — `:not()` evita pisar los
   íconos Material del botón de colapsar (V4.1). */
section[data-testid="stSidebar"] *:not([data-testid="stSidebarCollapseButton"]):not([data-testid="stSidebarCollapseButton"] *) {{
    color: {white} !important;
}}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 {{
    color: {white} !important;
}}
section[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: transparent !important;
    border: 2px solid {white} !important;
    color: {white} !important;
}}
section[data-testid="stSidebar"] button[kind="primary"] {{
    background-color: {magenta_primary} !important;
    border: 2px solid {white} !important;
    color: {white} !important;
}}

/* ── Tabs: texto oscuro por defecto, magenta cuando activo ── */
.stTabs [data-baseweb="tab"] {{
    color: {gray_dark} !important;
    font-weight: 600;
}}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"],
.stTabs [aria-selected="true"] {{
    color: {magenta_primary} !important;
    border-bottom: 3px solid {magenta_primary} !important;
}}

/* ── Métricas / KPIs ── */
[data-testid="metric-container"],
[data-testid="stMetric"] {{
    background-color: {white};
    border-left: 4px solid {magenta_primary};
    border-radius: 8px;
    padding: 12px 16px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}}
[data-testid="metric-container"] label,
[data-testid="stMetricLabel"] {{
    color: {gray_medium} !important;
    font-size: 0.82rem !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"],
[data-testid="stMetricValue"] {{
    color: {gray_dark} !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}}

/* ── Tarjeta de fondo/estrato (legalizados desglosados, V2.4) ── */
.tarjeta-fondo {{
    background-color: {white};
    border: 1px solid #E0E0E0;
    border-top: 4px solid {magenta_primary};
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
    min-height: 150px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.tarjeta-fondo h4 {{
    color: {magenta_dark} !important;
    font-size: 0.9rem !important;
    font-weight: 700;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: break-word;
    line-height: 1.3;
    margin: 0 0 10px 0;
}}
.tarjeta-fondo .valor-principal {{
    color: {gray_dark} !important;
    font-size: 1.7rem;
    font-weight: 800;
    line-height: 1;
}}
.tarjeta-fondo .etiqueta {{
    color: {gray_medium} !important;
    font-size: 0.78rem;
    margin-top: 6px;
}}

/* ── Botones ── */
.stButton > button {{
    background-color: {magenta_primary} !important;
    color: {white} !important;
    border: none;
    border-radius: 6px;
    font-weight: 600;
}}
.stButton > button:hover {{
    background-color: {magenta_dark} !important;
    color: {white} !important;
}}
.stButton > button[kind="primary"] {{
    background-color: {magenta_primary} !important;
    border-color: {magenta_primary} !important;
    color: {white} !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color: {magenta_dark} !important;
    border-color: {magenta_dark} !important;
}}

/* ── Links ── */
a, a:visited {{ color: {magenta_primary}; }}
a:hover {{ color: {magenta_dark}; }}

/* ── Expander hover ── */
[data-testid="stExpander"] summary:hover {{ color: {magenta_primary} !important; }}
</style>
"""


def inject_global_css() -> None:
    """Inyecta el CSS global con la paleta Sapiencia en la app Streamlit."""
    import streamlit as st

    css = _GLOBAL_CSS_TEMPLATE.format(**SAPIENCIA_COLORS)
    st.markdown(css, unsafe_allow_html=True)
