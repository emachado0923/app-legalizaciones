"""Tarjetas visuales para el dashboard de recursos.

Implementa renderizado dinámico de tarjetas por fondo y estrato según
`CONFIGURACION_ESTRATOS_FONDOS` (Fase 4 del refactor).
"""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from app.config import CONFIGURACION_ESTRATOS_FONDOS, SAPIENCIA_COLORS
from app.utils import (
    escapar_html,
    format_currency,
    format_number_integer,
    get_badge_estado,
    get_color_utilizacion,
    get_comuna_numero,
)


# ---------------------------------------------------------------------------
# Helpers de estado por porcentaje de utilización
# ---------------------------------------------------------------------------
def _color_estado(porcentaje: float) -> str:
    """Color asociado al porcentaje de utilización."""
    if porcentaje >= 90:
        return SAPIENCIA_COLORS["error_red"]
    if porcentaje >= 70:
        return SAPIENCIA_COLORS["warning_amber"]
    if porcentaje >= 40:
        return SAPIENCIA_COLORS["success_green"]
    return "#0b8043"


def _texto_estado(porcentaje: float) -> tuple[str, str]:
    """Retorna `(clase_css, etiqueta)` del estado de utilización."""
    if porcentaje >= 90:
        return "urgent", "POTENCIALMENTE AGOTADO"
    if porcentaje >= 70:
        return "warning", "MODERADO"
    if porcentaje >= 40:
        return "ok", "DISPONIBLE"
    return "available", "MUY DISPONIBLE"


# ---------------------------------------------------------------------------
# CORRECCIÓN V2: Tarjeta de legalizados por segmento (desglose por fondo)
# ---------------------------------------------------------------------------
def render_tarjeta_legalizados_segmento(
    titulo: str,
    valor: int,
    icono: str = "🎓",
) -> None:
    """Tarjeta blanca con borde superior magenta para un segmento de legalizados.

    Usa la clase CSS `.tarjeta-fondo` inyectada globalmente (theme.py).
    Cumple regla de contraste: título en magenta_dark sobre fondo blanco.
    """
    # Convertir saltos de línea explícitos a <br> para HTML, pero respetar
    # white-space: pre-wrap del CSS.
    titulo_html = str(titulo).replace("\n", "<br>")
    valor_formateado = f"{int(valor):,}"
    st.markdown(
        f"""
        <div class="tarjeta-fondo">
            <h4>{icono} {titulo_html}</h4>
            <div>
                <div class="valor-principal">{valor_formateado}</div>
                <div class="etiqueta">legalizados</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tarjeta de métrica simple (para métricas superiores)
# ---------------------------------------------------------------------------
def render_tarjeta_metrica(
    titulo: str,
    valor: str,
    descripcion: str = "",
    color_borde: str | None = None,
    icono: str = "📊",
) -> None:
    """Renderiza una tarjeta con título, valor grande y descripción."""
    borde = color_borde or SAPIENCIA_COLORS["magenta_primary"]
    st.markdown(
        f"""
        <div style='
            background: white;
            border-radius: 15px;
            padding: 25px 15px;
            text-align: center;
            border: 2px solid {borde};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <div style='font-size: 16px; color: {SAPIENCIA_COLORS["gray_medium"]};
                       font-weight: 700; margin-bottom: 15px;'>
                {icono} {titulo}
            </div>
            <div style='font-size: 28px; color: {borde}; font-weight: 900;
                       line-height: 1.2; word-break: break-word;'>
                {valor}
            </div>
            <div style='font-size: 14px; color: #80868b; margin-top: 12px;'>
                {descripcion}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Tarjeta de resumen por estrato (un bloque por fondo)
# ---------------------------------------------------------------------------
def _tarjeta_estrato_html(
    label: str,
    presupuesto: int,
    restante: int,
    usuarios: int,
    porcentaje: float,
    has_data: bool,
) -> str:
    """HTML de una tarjeta de resumen para un rango de estratos."""
    if not has_data:
        return f"""
        <div class="estrato-resumen-card no-data">
            <div class="estrato-resumen-header">
                <div class="estrato-resumen-title">{label}</div>
                <div class="estrato-resumen-badge">RESUMEN</div>
            </div>
            <div class="no-data-state">
                <div class="no-data-icon">📭</div>
                <div class="no-data-title">NO APLICA</div>
                <div class="no-data-text">No hay datos para {label}</div>
            </div>
        </div>
        """

    bar_color = _color_estado(porcentaje)
    urgency_class, urgency_text = _texto_estado(porcentaje)

    return f"""
    <div class="estrato-resumen-card {urgency_class}">
        <div class="estrato-resumen-header">
            <div class="estrato-resumen-title">{label}</div>
            <div class="estrato-resumen-badge">RESUMEN</div>
        </div>
        <div class="estrato-resumen-status {urgency_class}">
            <span class="estrato-resumen-status-text">{urgency_text}</span>
        </div>
        <div class="estrato-resumen-metrics">
            <div class="estrato-metric-row">
                <span class="estrato-metric-label">Presupuesto Total</span>
                <span class="estrato-metric-value">{format_currency(presupuesto)}</span>
            </div>
            <div class="estrato-metric-row">
                <span class="estrato-metric-label" style="color: {SAPIENCIA_COLORS['magenta_primary']};">Restante</span>
                <span class="estrato-metric-value" style="color: {SAPIENCIA_COLORS['magenta_primary']};">{format_currency(restante)}</span>
            </div>
            <div class="estrato-metric-row">
                <span class="estrato-metric-label" style="color: {SAPIENCIA_COLORS['success_green']};">Legalizados</span>
                <span class="estrato-metric-value" style="color: {SAPIENCIA_COLORS['success_green']};">{format_number_integer(usuarios)}</span>
            </div>
        </div>
        <div class="estrato-resumen-progress">
            <div class="estrato-resumen-progress-info">
                <span class="estrato-resumen-progress-label">Utilización</span>
                <span class="estrato-resumen-progress-value" style="color: {bar_color};">{porcentaje:.1f}%</span>
            </div>
            <div class="estrato-resumen-progress-bar">
                <div class="estrato-resumen-progress-fill" style="width: {porcentaje}%; background: {bar_color};"></div>
            </div>
        </div>
    </div>
    """


# ---------------------------------------------------------------------------
# Filtros de datos por configuración de fondo
# ---------------------------------------------------------------------------
def _filtrar_estrato(df_fondo: pd.DataFrame, estratos: List[int]) -> pd.DataFrame:
    """Filtra `df_fondo` para quedarse con las filas cuyo estrato esté en la lista.

    Estrategia (en orden):
    1. Si existe columna `estrato_rango` ("1-3" / "4-6" / None), úsala.
    2. Si existe columna `estrato` (entero), filtra directo.
    3. Sin información de estrato, retorna `df_fondo` sin filtrar (caso de
       fondos cuyo único rango son "Estratos 1-6", p.ej. posgrados).
    """
    if df_fondo.empty:
        return df_fondo

    quiere_1_3 = any(e in {1, 2, 3} for e in estratos)
    quiere_4_6 = any(e in {4, 5, 6} for e in estratos)

    if "estrato_rango" in df_fondo.columns:
        rangos_validos: list[str] = []
        if quiere_1_3:
            rangos_validos.append("1-3")
        if quiere_4_6:
            rangos_validos.append("4-6")

        # Filas con `estrato_rango` nulo se incluyen cuando la tarjeta cubre
        # el rango completo (p.ej. "Estratos 1-6" en posgrado).
        mask = df_fondo["estrato_rango"].isin(rangos_validos)
        if quiere_1_3 and quiere_4_6:
            mask = mask | df_fondo["estrato_rango"].isna()
        if mask.any():
            return df_fondo[mask]
        # Si ninguna fila coincide pero la tarjeta es 1-6 completa, devolver todo.
        if quiere_1_3 and quiere_4_6:
            return df_fondo
        return df_fondo.iloc[0:0]

    if "estrato" in df_fondo.columns:
        return df_fondo[df_fondo["estrato"].isin(estratos)]

    return df_fondo


def _resumen_fila(df_estrato: pd.DataFrame) -> Dict[str, Any]:
    """Calcula presupuesto/restante/usuarios/% para un subset."""
    if df_estrato.empty:
        return {"presupuesto": 0, "restante": 0, "usuarios": 0, "porcentaje": 0.0, "has_data": False}

    presupuesto = int(df_estrato["presupuesto_comuna"].sum()) if "presupuesto_comuna" in df_estrato.columns else 0
    restante = int(df_estrato["restante_presupuesto_comuna"].sum()) if "restante_presupuesto_comuna" in df_estrato.columns else 0
    usuarios = int(df_estrato["numero_usuarios_comuna"].sum()) if "numero_usuarios_comuna" in df_estrato.columns else 0
    consumido = presupuesto - restante
    porcentaje = (consumido / presupuesto * 100) if presupuesto > 0 else 0.0

    return {
        "presupuesto": presupuesto,
        "restante": restante,
        "usuarios": usuarios,
        "porcentaje": porcentaje,
        "has_data": presupuesto > 0 or usuarios > 0,
    }


# ---------------------------------------------------------------------------
# CSS embebido (modernizado a paleta Sapiencia)
# ---------------------------------------------------------------------------
def _css_cards() -> str:
    """CSS para las tarjetas dinámicas (paleta Sapiencia)."""
    magenta_primary = SAPIENCIA_COLORS["magenta_primary"]
    magenta_dark = SAPIENCIA_COLORS["magenta_dark"]
    gray_dark = SAPIENCIA_COLORS["gray_dark"]

    return f"""
    <style>
    .cards-container * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Calibri', Arial, sans-serif !important;
    }}
    .fondo-sections {{
        display: flex;
        flex-direction: column;
        gap: 30px;
        padding: 10px 0;
    }}
    .fondo-section {{
        background: white;
        border-radius: 18px;
        padding: 0;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
        border: 2px solid #e0e0e0;
        overflow: hidden;
    }}
    .fondo-section-header {{
        background: linear-gradient(135deg, {magenta_primary} 0%, {magenta_dark} 100%);
        padding: 14px 26px;
        display: flex;
        align-items: center;
        gap: 18px;
    }}
    .fondo-section-numero {{
        font-size: 32px !important;
        font-weight: 900 !important;
        color: white !important;
        background: rgba(255, 255, 255, 0.2);
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .fondo-section-nombre {{
        font-size: 22px !important;
        font-weight: 800 !important;
        color: white !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        flex-grow: 1;
    }}
    .fondo-section-tag {{
        background: rgba(255, 255, 255, 0.18);
        color: white !important;
        padding: 6px 12px;
        border-radius: 14px;
        font-size: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }}
    .estrato-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        gap: 0;
        border-top: 2px solid #f0f0f0;
    }}
    .estrato-resumen-card {{
        padding: 22px;
        min-height: 260px;
        display: flex;
        flex-direction: column;
        background: #fafafa;
        border-right: 2px solid #f0f0f0;
    }}
    .estrato-resumen-card.urgent {{
        border-left: 5px solid {SAPIENCIA_COLORS['error_red']};
        background: linear-gradient(135deg, #ffffff 0%, #fce8e6 100%);
    }}
    .estrato-resumen-card.warning {{
        border-left: 5px solid {SAPIENCIA_COLORS['warning_amber']};
        background: linear-gradient(135deg, #ffffff 0%, #fef7e0 100%);
    }}
    .estrato-resumen-card.ok {{
        border-left: 5px solid {SAPIENCIA_COLORS['success_green']};
        background: linear-gradient(135deg, #ffffff 0%, #e6f4ea 100%);
    }}
    .estrato-resumen-card.available {{
        border-left: 5px solid #0b8043;
        background: linear-gradient(135deg, #ffffff 0%, #d5e8d9 100%);
    }}
    .estrato-resumen-card.no-data {{
        background: #f8f9fa;
        justify-content: center;
        align-items: center;
        border-left: 5px solid #80868b;
    }}
    .no-data-state {{ text-align: center; padding: 20px; }}
    .no-data-icon {{ font-size: 42px; margin-bottom: 12px; opacity: 0.5; }}
    .no-data-title {{
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #80868b !important;
        margin-bottom: 8px;
        text-transform: uppercase;
    }}
    .no-data-text {{ font-size: 14px; color: #9aa0a6; }}
    .estrato-resumen-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }}
    .estrato-resumen-title {{
        font-size: 20px !important;
        font-weight: 800 !important;
        color: {gray_dark} !important;
    }}
    .estrato-resumen-badge {{
        padding: 5px 10px;
        border-radius: 12px;
        font-size: 11px !important;
        font-weight: 700 !important;
        background-color: #fce8f4;
        color: {magenta_primary} !important;
        border: 2px solid {magenta_primary};
        text-transform: uppercase;
    }}
    .estrato-resumen-status {{
        padding: 8px;
        border-radius: 10px;
        font-size: 16px !important;
        font-weight: 800 !important;
        text-align: center;
        margin: 12px 0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}
    .estrato-resumen-status.urgent {{ background-color: {SAPIENCIA_COLORS['error_red']}; color: white !important; }}
    .estrato-resumen-status.warning {{ background-color: {SAPIENCIA_COLORS['warning_amber']}; color: {gray_dark} !important; }}
    .estrato-resumen-status.ok {{ background-color: {SAPIENCIA_COLORS['success_green']}; color: white !important; }}
    .estrato-resumen-status.available {{ background-color: #0b8043; color: white !important; }}
    .estrato-resumen-metrics {{
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 10px;
    }}
    .estrato-metric-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .estrato-metric-label {{
        font-size: 14px !important;
        color: #5f6368;
        font-weight: 600;
    }}
    .estrato-metric-value {{
        font-size: 16px !important;
        font-weight: 700 !important;
        color: {gray_dark};
        text-align: right;
    }}
    .estrato-resumen-progress {{ margin-top: 16px; }}
    .estrato-resumen-progress-info {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
    }}
    .estrato-resumen-progress-label {{
        font-size: 13px !important;
        color: #5f6368;
        font-weight: 600;
    }}
    .estrato-resumen-progress-value {{
        font-size: 18px !important;
        font-weight: 900 !important;
    }}
    .estrato-resumen-progress-bar {{
        height: 10px;
        background-color: #eaedf2;
        border-radius: 5px;
        overflow: hidden;
        border: 1px solid #dadce0;
    }}
    .estrato-resumen-progress-fill {{
        height: 100%;
        border-radius: 5px;
        transition: width 1s ease;
    }}
    @media (max-width: 900px) {{
        .estrato-grid {{ grid-template-columns: 1fr; }}
    }}
    </style>
    """


# ---------------------------------------------------------------------------
# Render principal — tarjetas dinámicas por fondo
# ---------------------------------------------------------------------------
def render_tarjetas_por_fondo(df: pd.DataFrame, fondo: str) -> None:
    """Renderiza las tarjetas correspondientes a un fondo específico.

    Lee la configuración de tarjetas desde `CONFIGURACION_ESTRATOS_FONDOS`
    y genera una tarjeta por cada entrada `tarjetas[*]` definida para
    ese fondo.

    Args:
        df: DataFrame de presupuesto ya filtrado por el fondo a renderizar.
        fondo: clave en `CONFIGURACION_ESTRATOS_FONDOS` (ej. "RECURSO ORDINARIO").
    """
    config = CONFIGURACION_ESTRATOS_FONDOS.get(fondo)
    if not config:
        st.warning(f"⚠️ El fondo '{fondo}' no está configurado en CONFIGURACION_ESTRATOS_FONDOS")
        return

    tarjetas_html: List[str] = []
    for tarjeta in config["tarjetas"]:
        df_tarjeta = _filtrar_estrato(df, tarjeta["estratos"])
        resumen = _resumen_fila(df_tarjeta)
        tarjetas_html.append(
            _tarjeta_estrato_html(
                label=tarjeta["label"],
                presupuesto=resumen["presupuesto"],
                restante=resumen["restante"],
                usuarios=resumen["usuarios"],
                porcentaje=resumen["porcentaje"],
                has_data=resumen["has_data"],
            )
        )

    tipo_label = config["tipo"].upper().replace("_", " ")
    html_content = f"""
    <!DOCTYPE html>
    <html><head><meta charset="UTF-8">{_css_cards()}</head>
    <body>
        <div class="cards-container">
            <div class="fondo-section">
                <div class="fondo-section-header">
                    <div class="fondo-section-numero">📦</div>
                    <div class="fondo-section-nombre">{fondo}</div>
                    <div class="fondo-section-tag">{tipo_label}</div>
                </div>
                <div class="estrato-grid">
                    {''.join(tarjetas_html)}
                </div>
            </div>
        </div>
    </body></html>
    """
    altura = 360 + (max(0, len(config["tarjetas"]) - 1) * 60)
    components.html(html_content, height=altura, scrolling=False)


def render_tarjetas_recurso_comunas(df: pd.DataFrame, fondos_visibles: List[str] | None = None) -> None:
    """Renderiza todas las tarjetas dinámicas por fondo según el DataFrame.

    Args:
        df: DataFrame de presupuesto (debe contener `fuente_financiacion`
            o equivalente).
        fondos_visibles: lista de fondos a renderizar. Si es None usa todos
            los presentes en el DataFrame que estén configurados.
    """
    if df.empty:
        st.info("📭 No hay datos de presupuesto para mostrar.")
        return

    if "fuente_financiacion" not in df.columns:
        st.warning(
            "⚠️ El DataFrame no tiene columna `fuente_financiacion`. "
            "No se pueden renderizar tarjetas dinámicas. "
            f"Columnas disponibles: {list(df.columns)}"
        )
        return

    fondos_en_datos = sorted(df["fuente_financiacion"].dropna().unique().tolist())
    if fondos_visibles is None:
        fondos_visibles = [f for f in fondos_en_datos if f in CONFIGURACION_ESTRATOS_FONDOS]

    if not fondos_visibles:
        st.info("📭 Ningún fondo coincide con la configuración activa.")
        return

    # Mostrar leyenda
    with st.expander("📋 LEYENDA - ESTADOS DE UTILIZACIÓN", expanded=False):
        cols = st.columns(4)
        estados = [
            ("POTENCIALMENTE AGOTADO", ">= 90% usado", SAPIENCIA_COLORS["error_red"], "#fce8e6"),
            ("MODERADO", "70-89% usado", SAPIENCIA_COLORS["warning_amber"], "#fef7e0"),
            ("DISPONIBLE", "40-70% usado", SAPIENCIA_COLORS["success_green"], "#e6f4ea"),
            ("MUY DISPONIBLE", "< 40% usado", "#0b8043", "#d5e8d9"),
        ]
        for idx, (nombre, desc, color, bg) in enumerate(estados):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 10px; background: {bg};
                             border-radius: 8px; border: 2px solid {color};">
                        <div style="font-weight: 900; color: {color}; font-size: 14px;">{nombre}</div>
                        <div style="color: #666; font-size: 12px;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    for fondo in fondos_visibles:
        df_fondo = df[df["fuente_financiacion"] == fondo]
        if df_fondo.empty:
            continue
        render_tarjetas_por_fondo(df_fondo, fondo)


# ===========================================================================
# CORRECCIÓN V3: tarjeta con desglose por fiducia (panel resumen + fiducias)
# ===========================================================================
def agrupar_para_resumen_estrato(df: pd.DataFrame, grupo_key: Dict[str, Any]) -> Dict[str, Any]:
    """Resume un subconjunto del df por (fondo, comuna, estrato_rango).

    Args:
        df: DataFrame de presupuesto ya procesado (con `fuente_financiacion`,
            `comuna`, `estrato_rango`, `idfiducia`).
        grupo_key: claves para filtrar. Soporta:
            - `fondo` (= `fuente_financiacion`)
            - `comuna` (valor crudo)
            - `grupo_estrato` (label "1-3" / "4-6" / "1-4" / "1-6" / None)
              o `estrato_rango` (valor crudo de la columna).

    Returns:
        Dict con `presupuesto_total`, `restante`, `consumido`, `legalizados`,
        `pct_uso` y `fiducias` (lista por idfiducia).
    """
    if df is None or df.empty:
        return {
            "presupuesto_total": 0, "restante": 0, "consumido": 0,
            "legalizados": 0, "pct_uso": 0.0, "fiducias": [],
        }

    mask = pd.Series(True, index=df.index)
    fondo = grupo_key.get("fondo")
    comuna = grupo_key.get("comuna")
    estrato_rango = grupo_key.get("estrato_rango")
    grupo_estrato_label = grupo_key.get("grupo_estrato")

    if fondo is not None and "fuente_financiacion" in df.columns:
        mask &= df["fuente_financiacion"] == fondo
    if comuna is not None and "comuna" in df.columns:
        mask &= df["comuna"].astype(str) == str(comuna)
    if estrato_rango is not None and "estrato_rango" in df.columns:
        # Comparación tolerante a NaN
        if pd.isna(estrato_rango):
            mask &= df["estrato_rango"].isna()
        else:
            mask &= df["estrato_rango"] == estrato_rango

    sub = df[mask]

    presupuesto_total = int(sub.get("presupuesto_comuna", pd.Series(dtype=int)).fillna(0).sum())
    restante = int(sub.get("restante_presupuesto_comuna", pd.Series(dtype=int)).fillna(0).sum())
    consumido = presupuesto_total - restante
    legalizados = int(sub.get("numero_usuarios_comuna", pd.Series(dtype=int)).fillna(0).sum())
    pct_uso = (consumido / presupuesto_total * 100) if presupuesto_total > 0 else 0.0

    fiducias: List[Dict[str, Any]] = []
    if not sub.empty and "idfiducia" in sub.columns:
        # Agrupar por idfiducia por si hay duplicados (no esperado pero defensivo)
        for fid_id, grupo_fid in sub.groupby("idfiducia", dropna=False):
            pres_fid = int(grupo_fid.get("presupuesto_comuna", pd.Series(dtype=int)).fillna(0).sum())
            rest_fid = int(grupo_fid.get("restante_presupuesto_comuna", pd.Series(dtype=int)).fillna(0).sum())
            pct_fid = ((pres_fid - rest_fid) / pres_fid * 100) if pres_fid > 0 else 0.0
            fiducias.append({
                "id": int(fid_id) if pd.notna(fid_id) else None,
                "nombre": f"Fiducia {int(fid_id)}" if pd.notna(fid_id) else "Sin fiducia",
                "presupuesto": pres_fid,
                "restante": rest_fid,
                "pct_uso": pct_fid,
            })
        # Ordenar por presupuesto descendente
        fiducias.sort(key=lambda x: x["presupuesto"], reverse=True)

    return {
        "presupuesto_total": presupuesto_total,
        "restante": restante,
        "consumido": consumido,
        "legalizados": legalizados,
        "pct_uso": pct_uso,
        "fiducias": fiducias,
        "grupo_estrato_label": grupo_estrato_label,
    }


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convierte `#RRGGBB` a `rgba(r, g, b, alpha)`."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return f"rgba(0, 0, 0, {alpha})"
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _html_fiducia_item(fid: Dict[str, Any]) -> str:
    """HTML de una tarjetita individual de fiducia (1 sola línea, sin blank lines).

    CORRECCIÓN V4: previo a este cambio, los f-strings multilínea con sangría
    creaban blank lines que Streamlit interpretaba como fin de bloque HTML,
    haciendo visible el código fuente como texto plano.
    """
    pct = fid["pct_uso"]
    color_pct = get_color_utilizacion(pct)
    pct_bar = max(0, min(100, pct))
    nombre = escapar_html(fid["nombre"])
    pres = escapar_html(format_currency(fid["presupuesto"]))
    rest = escapar_html(format_currency(fid["restante"]))
    return (
        "<div style=\"background:#FFFFFF;border:1px solid #E0E0E0;border-radius:8px;"
        "padding:12px 14px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,0.05);\">"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;\">"
        f"<span style=\"font-weight:700;font-size:14px;color:#3D3D3D;\">{nombre}</span>"
        f"<span style=\"font-weight:800;font-size:14px;color:{color_pct};\">{pct:.1f}%</span>"
        "</div>"
        "<div style=\"display:flex;justify-content:space-between;margin-bottom:6px;font-size:11px;color:#6B6B6B;\">"
        f"<div>Presupuesto<br><strong style=\"color:#3D3D3D;font-size:13px;\">{pres}</strong></div>"
        f"<div style=\"text-align:right;\">Restante<br><strong style=\"color:#3D3D3D;font-size:13px;\">{rest}</strong></div>"
        "</div>"
        "<div style=\"height:5px;background:#EAEDF2;border-radius:3px;overflow:hidden;\">"
        f"<div style=\"height:100%;width:{pct_bar:.1f}%;background:{color_pct};border-radius:3px;transition:width 0.6s ease;\"></div>"
        "</div>"
        "</div>"
    )


def render_tarjeta_estrato_con_fiducias(
    nombre_comuna: str,
    numero_comuna: str,
    grupo_estrato: str,
    datos: Dict[str, Any],
    color_header: str = "#7D1860",
) -> None:
    """Renderiza una tarjeta de estrato con panel resumen + desglose de fiducias.

    CORRECCIÓN V4: el HTML se construye como UNA SOLA string sin saltos de línea
    internos para evitar que Markdown interprete líneas en blanco (causadas por
    interpolaciones vacías como `numero_comuna == ""`) como fin de bloque HTML.
    También se sanitizan todos los valores que vienen de variables.
    """
    # --- Sanitización y normalización ---
    nombre_safe = escapar_html(nombre_comuna)
    numero_safe = escapar_html(numero_comuna)
    estrato_safe = escapar_html(grupo_estrato)
    color_header_safe = escapar_html(color_header)

    pct = float(datos.get("pct_uso") or 0.0)
    badge = get_badge_estado(pct)
    color_pct = get_color_utilizacion(pct)
    bg_panel = _hex_to_rgba(badge["bg"], 0.10)
    pct_bar = max(0, min(100, pct))

    pres_fmt = escapar_html(format_currency(datos.get("presupuesto_total", 0) or 0))
    rest_fmt = escapar_html(format_currency(datos.get("restante", 0) or 0))
    leg_fmt = escapar_html(format_number_integer(datos.get("legalizados", 0) or 0))

    badge_bg = escapar_html(badge["bg"])
    badge_text = escapar_html(badge["text"])
    badge_label = escapar_html(badge["label"])

    fiducias = datos.get("fiducias", []) or []
    n_fid = len(fiducias)
    fiducias_html = "".join(_html_fiducia_item(f) for f in fiducias)
    if not fiducias_html:
        fiducias_html = (
            "<div style=\"text-align:center;padding:30px 10px;color:#9AA0A6;\">"
            "<div style=\"font-size:36px;opacity:0.5;\">📭</div>"
            "<div style=\"font-size:13px;margin-top:8px;\">Sin fiducias para este estrato</div>"
            "</div>"
        )

    # --- Header de comuna: cuando no hay número se omite el círculo ---
    if numero_safe.strip():
        cabecera_numero = (
            "<div style=\"font-size:22px;font-weight:900;color:#FFFFFF;"
            "background:rgba(255,255,255,0.18);width:44px;height:44px;border-radius:50%;"
            "display:flex;align-items:center;justify-content:center;margin-right:14px;flex-shrink:0;\">"
            f"{numero_safe}</div>"
        )
    else:
        cabecera_numero = ""

    # --- HTML completo en UNA SOLA línea (sin saltos de línea ni indentación) ---
    panel_izquierdo = (
        f"<div style=\"flex:1 1 320px;min-width:300px;padding:20px;background:{bg_panel};border-left:4px solid {badge_bg};\">"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;\">"
        f"<span style=\"font-size:18px;font-weight:800;color:#3D3D3D;\">ESTRATOS {estrato_safe}</span>"
        f"<span style=\"padding:4px 10px;font-size:11px;font-weight:700;background:#FCE8F4;color:#7D1860;border:2px solid #AB2181;border-radius:12px;text-transform:uppercase;\">RESUMEN</span>"
        "</div>"
        f"<div style=\"background:{badge_bg};color:{badge_text};padding:8px 12px;border-radius:8px;text-align:center;font-size:14px;font-weight:800;letter-spacing:0.8px;text-transform:uppercase;margin-bottom:14px;\">{badge_label}</div>"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(0,0,0,0.06);\">"
        "<span style=\"font-size:13px;color:#6B6B6B;font-weight:600;\">Presupuesto Total</span>"
        f"<span style=\"font-size:14px;color:#3D3D3D;font-weight:700;\">{pres_fmt}</span>"
        "</div>"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(0,0,0,0.06);\">"
        "<span style=\"font-size:13px;color:#AB2181;font-weight:600;\">Restante</span>"
        f"<span style=\"font-size:14px;color:#AB2181;font-weight:700;\">{rest_fmt}</span>"
        "</div>"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid rgba(0,0,0,0.06);\">"
        "<span style=\"font-size:13px;color:#2E7D32;font-weight:600;\">Legalizados</span>"
        f"<span style=\"font-size:14px;color:#2E7D32;font-weight:700;\">{leg_fmt}</span>"
        "</div>"
        "<div style=\"margin-top:14px;\">"
        "<div style=\"display:flex;justify-content:space-between;margin-bottom:6px;\">"
        "<span style=\"font-size:12px;color:#6B6B6B;font-weight:600;\">Utilización</span>"
        f"<span style=\"font-size:16px;color:{color_pct};font-weight:900;\">{pct:.1f}%</span>"
        "</div>"
        "<div style=\"height:9px;background:#EAEDF2;border-radius:5px;overflow:hidden;border:1px solid #DADCE0;\">"
        f"<div style=\"height:100%;width:{pct_bar:.1f}%;background:{color_pct};border-radius:5px;transition:width 0.8s ease;\"></div>"
        "</div>"
        "</div>"
        "</div>"
    )

    panel_derecho = (
        "<div style=\"flex:1 1 320px;min-width:300px;padding:20px;background:#FAFAFA;\">"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid #F0F0F0;\">"
        f"<span style=\"font-size:16px;font-weight:800;color:#AB2181;\">📦 FIDUCIAS ESTRATOS {estrato_safe}</span>"
        f"<span style=\"font-size:12px;font-weight:600;color:#6B6B6B;background:#F0F2F6;padding:3px 10px;border-radius:12px;\">{n_fid} fiducia(s)</span>"
        "</div>"
        f"{fiducias_html}"
        "</div>"
    )

    html = (
        "<div style=\"border-radius:14px;overflow:hidden;border:1px solid #E0E0E0;"
        "box-shadow:0 4px 14px rgba(0,0,0,0.06);background:#FFFFFF;margin-bottom:18px;\">"
        f"<div style=\"background:{color_header_safe};padding:12px 20px;color:#FFFFFF;display:flex;align-items:center;\">"
        f"{cabecera_numero}"
        f"<div style=\"font-size:18px;font-weight:800;letter-spacing:0.3px;flex-grow:1;color:#FFFFFF;\">{nombre_safe}</div>"
        "</div>"
        "<div style=\"display:flex;flex-wrap:wrap;\">"
        f"{panel_izquierdo}"
        f"{panel_derecho}"
        "</div>"
        "</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
