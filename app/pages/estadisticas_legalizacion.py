"""Página V5.10: Estadísticas de legalización de giros.

Fuente: `convocatoria_sapiencia.vw_giros_informe_total` filtrada por
`Convocatoria = '2026-2'`.

Estructura:
1. Segmentadores (multiselect fondo, selectbox pagaré, multiselect modalidad).
2. KPIs superiores (5 métricas).
3. Tarjetas por modalidad (3 tarjetas).
4. Tarjetas por tipo de beneficio (4 tarjetas).
5. Gráficos descriptivos (6 con Plotly).
6. Tabla detallada colapsable con descarga CSV.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.components.cards import render_tarjeta_metrica
from app.config import SAPIENCIA_COLORS, settings
from app.database import DatabaseError, fetch_giros_informe
from app.utils import format_currency, format_number_integer

# ---------------------------------------------------------------------------
# Constantes de la página
# ---------------------------------------------------------------------------
CONVOCATORIA_ACTIVA = "2026-2"

# V5.10: mapeo de valor de BD → etiqueta amigable con ícono
MAPA_FONDOS_DISPLAY: Dict[str, str] = {
    "BECAS MEJORES DEPORTISTAS": "🏅 Mejores Deportistas",
    "PUAP Línea de Crédito Condonable Pregrado con Recurso Ordinario y Fondo EPM.": "📚 Pregrado RO",
    "FONDO PRESUPUESTO PARTICIPATIVO": "🏘️ Pregrado PP",
    "FONDO FORMACION AVANZADA": "🎓 Formación Avanzada",
    "EXTENDIENDO FRONTERAS EDUCATIVAS PP": "🌎 Ext. Fronteras PP",
    "EXTENDIENDO FRONTERAS EDUCATIVAS RO": "🌍 Ext. Fronteras RO",
}

MODALIDADES: List[str] = ["Matricula", "Sostenimiento", "Matricula y sostenimiento"]

PALETA_MAGENTA = [
    SAPIENCIA_COLORS["magenta_primary"],
    SAPIENCIA_COLORS["magenta_dark"],
    SAPIENCIA_COLORS["magenta_light"],
    SAPIENCIA_COLORS["success_green"],
    SAPIENCIA_COLORS["warning_amber"],
    SAPIENCIA_COLORS["error_red"],
    SAPIENCIA_COLORS["gray_medium"],
]


# ---------------------------------------------------------------------------
# Carga y saneamiento de datos
# ---------------------------------------------------------------------------
@st.cache_data(ttl=settings.CACHE_TTL, show_spinner=False)
def _cargar_giros() -> pd.DataFrame:
    """Trae los registros filtrados por convocatoria y limpia tipos."""
    df = fetch_giros_informe(CONVOCATORIA_ACTIVA)
    if df.empty:
        return df

    # Normalizar columnas numéricas (BD las devuelve como int/decimal, pero
    # con NaN cuando el usuario no aplica al tipo de giro).
    for col in ("Valor_matricula", "Valor_sostenimiento"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    # Estrato numérico donde sea posible (para el gráfico PP × estrato)
    if "Estrato" in df.columns:
        df["Estrato"] = pd.to_numeric(df["Estrato"], errors="coerce")

    # Columna auxiliar: grupo de estrato 1-3 / 4-6 (para PP)
    if "Estrato" in df.columns:
        df["grupo_estrato"] = df["Estrato"].apply(
            lambda x: "1-3" if pd.notna(x) and x <= 3 else ("4-6" if pd.notna(x) else "N/D")
        )

    # Columna auxiliar: fondo con etiqueta legible
    if "fondo" in df.columns:
        df["fondo_display"] = df["fondo"].map(MAPA_FONDOS_DISPLAY).fillna(df["fondo"])

    # Clasificación de beneficio a partir de los dos valores
    df["clasificacion_beneficio"] = df.apply(_clasificar_beneficio, axis=1)

    return df


def _clasificar_beneficio(row: pd.Series) -> str:
    """Clasifica el tipo de beneficio entregado según valores de giro.

    - Valor_matricula > 0 y Valor_sostenimiento == 0 → 'Solo Matrícula'
    - Valor_matricula == 0 y Valor_sostenimiento > 0 → 'Solo Sostenimiento'
    - Ambos > 0 → 'Matrícula y Sostenimiento'
    - Ambos == 0 → 'Sin beneficio económico'
    """
    val_mat = row.get("Valor_matricula", 0) or 0
    val_sos = row.get("Valor_sostenimiento", 0) or 0
    if val_mat > 0 and val_sos > 0:
        return "Matrícula y Sostenimiento"
    if val_mat > 0:
        return "Solo Matrícula"
    if val_sos > 0:
        return "Solo Sostenimiento"
    return "Sin beneficio económico"


# ---------------------------------------------------------------------------
# Filtros (barra superior)
# ---------------------------------------------------------------------------
def _renderizar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza los 3 filtros y retorna el DataFrame filtrado."""
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            fondos_opciones = sorted(df["fondo"].dropna().unique().tolist())
            fondos_sel = st.multiselect(
                "🎯 Fondo",
                options=fondos_opciones,
                default=fondos_opciones,
                format_func=lambda v: MAPA_FONDOS_DISPLAY.get(v, v),
                help="Filtra por uno o varios fondos.",
                key="est_filtro_fondo",
            )

        with col2:
            pagare_opciones = ["Todos"] + sorted(df["Pagare"].dropna().unique().tolist())
            pagare_sel = st.selectbox(
                "📄 Estado Pagaré",
                options=pagare_opciones,
                key="est_filtro_pagare",
            )

        with col3:
            modalidades_presentes = [m for m in MODALIDADES if m in df["Tipo_solicitud_definitiva"].unique()]
            modalidades_sel = st.multiselect(
                "🧾 Modalidad",
                options=modalidades_presentes,
                default=modalidades_presentes,
                help="Filtra por modalidad de solicitud (matrícula, sostenimiento o ambas).",
                key="est_filtro_modalidad",
            )

    sub = df.copy()
    if fondos_sel:
        sub = sub[sub["fondo"].isin(fondos_sel)]
    if pagare_sel != "Todos":
        sub = sub[sub["Pagare"] == pagare_sel]
    if modalidades_sel:
        sub = sub[sub["Tipo_solicitud_definitiva"].isin(modalidades_sel)]

    return sub


# ---------------------------------------------------------------------------
# Sección 2 — KPIs superiores
# ---------------------------------------------------------------------------
def _renderizar_kpis(df: pd.DataFrame) -> None:
    """Renderiza 5 métricas superiores."""
    total = len(df)
    con_pagare_fmt = int((df["Pagare"] == "Pagare aprobado").sum()) + int((df["Pagare"] == "Pagare entregado").sum())
    sin_pagare = int((df["Pagare"] == "Sin entregar pagare").sum())
    total_matricula = int(df.get("Valor_matricula", pd.Series(dtype=int)).sum())
    total_sostenimiento = int(df.get("Valor_sostenimiento", pd.Series(dtype=int)).sum())

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_tarjeta_metrica("Total Legalizados", format_number_integer(total), "Registros en la convocatoria",
                                SAPIENCIA_COLORS["magenta_primary"], "👥")
    with c2:
        render_tarjeta_metrica("Con Pagaré", format_number_integer(con_pagare_fmt),
                                "Aprobados + entregados", SAPIENCIA_COLORS["success_green"], "✅")
    with c3:
        render_tarjeta_metrica("Sin Pagaré", format_number_integer(sin_pagare), "Pendientes de entrega",
                                SAPIENCIA_COLORS["warning_amber"], "⏳")
    with c4:
        render_tarjeta_metrica("Valor Matrícula", format_currency(total_matricula), "Suma girada",
                                SAPIENCIA_COLORS["magenta_dark"], "💰")
    with c5:
        render_tarjeta_metrica("Valor Sostenimiento", format_currency(total_sostenimiento), "Suma girada",
                                SAPIENCIA_COLORS["magenta_dark"], "💵")


# ---------------------------------------------------------------------------
# Sección 3 — Tarjetas por modalidad
# ---------------------------------------------------------------------------
def _renderizar_modalidades(df: pd.DataFrame) -> None:
    """3 tarjetas: conteo por Tipo_solicitud_definitiva."""
    st.markdown(
        f"<h3 style='color:{SAPIENCIA_COLORS['magenta_primary']};margin-top:16px;'>"
        "🧾 Distribución por modalidad</h3>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    columnas = [c1, c2, c3]
    iconos = ["📚", "💵", "🧾"]
    for col, mod, icono in zip(columnas, MODALIDADES, iconos):
        conteo = int((df["Tipo_solicitud_definitiva"] == mod).sum())
        with col:
            render_tarjeta_metrica(mod.upper(), format_number_integer(conteo),
                                    "solicitudes", SAPIENCIA_COLORS["magenta_primary"], icono)


# ---------------------------------------------------------------------------
# Sección 4 — Tarjetas de beneficios entregados
# ---------------------------------------------------------------------------
def _renderizar_beneficios(df: pd.DataFrame) -> None:
    """3 tarjetas: conteo y valor total por tipo de beneficio (INCLUSIVO).

    V5.1: la lógica es INCLUSIVA — un beneficiario con matrícula y
    sostenimiento cuenta en ambas tarjetas. La suma puede superar el total.
    """
    st.markdown(
        f"<h3 style='color:{SAPIENCIA_COLORS['magenta_primary']};margin-top:16px;'>"
        "💳 Beneficios entregados</h3>",
        unsafe_allow_html=True,
    )

    val_mat = df.get("Valor_matricula", pd.Series(dtype=int))
    val_sos = df.get("Valor_sostenimiento", pd.Series(dtype=int))

    beneficios_matricula = df[val_mat > 0]
    beneficios_sostenimiento = df[val_sos > 0]

    # V5.2: totales agregados (suma de las dos tarjetas anteriores)
    total_beneficios = len(beneficios_matricula) + len(beneficios_sostenimiento)
    monto_total = int(beneficios_matricula["Valor_matricula"].sum()) + int(
        beneficios_sostenimiento["Valor_sostenimiento"].sum()
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        render_tarjeta_metrica(
            "MATRÍCULA",
            format_number_integer(len(beneficios_matricula)),
            f"Total: {format_currency(int(beneficios_matricula['Valor_matricula'].sum()))}",
            SAPIENCIA_COLORS["magenta_primary"],
            "📘",
        )
    with c2:
        render_tarjeta_metrica(
            "SOSTENIMIENTO",
            format_number_integer(len(beneficios_sostenimiento)),
            f"Total: {format_currency(int(beneficios_sostenimiento['Valor_sostenimiento'].sum()))}",
            SAPIENCIA_COLORS["magenta_primary"],
            "🏠",
        )
    with c3:
        render_tarjeta_metrica(
            "TOTAL DE BENEFICIOS",
            format_number_integer(total_beneficios),
            f"Total: {format_currency(monto_total)}",
            SAPIENCIA_COLORS["magenta_primary"],
            "📊",
        )

    st.caption(
        "* Matrícula y Sostenimiento cuentan los beneficiarios con ese tipo de apoyo "
        "(un mismo beneficiario puede tener ambos). "
        "Total de Beneficios es la suma de ambas tarjetas."
    )


# ---------------------------------------------------------------------------
# Sección 5 — Gráficos Plotly
# ---------------------------------------------------------------------------
def _aplicar_tema(fig: go.Figure) -> go.Figure:
    """Tema visual Sapiencia común a todos los gráficos."""
    fig.update_layout(
        font_family="Calibri, Arial, sans-serif",
        font_color=SAPIENCIA_COLORS["gray_dark"],
        title_font_color=SAPIENCIA_COLORS["magenta_primary"],
        title_font_size=15,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        colorway=PALETA_MAGENTA,
    )
    return fig


def _mostrar_o_vacio(fig: go.Figure, df_grafico: pd.DataFrame, msg: str = "Sin datos para los filtros seleccionados") -> None:
    """Muestra la figura o un info si el df subyacente está vacío."""
    if df_grafico.empty:
        st.info(f"📭 {msg}")
        return
    st.plotly_chart(fig, use_container_width=True)


def _grafico_barras_fondo(df: pd.DataFrame) -> None:
    agg = df.groupby("fondo_display", as_index=False).size().rename(columns={"size": "conteo"})
    agg = agg.sort_values("conteo", ascending=True)
    fig = px.bar(
        agg, x="conteo", y="fondo_display", orientation="h",
        title="Legalizados por Fondo", text="conteo",
        labels={"fondo_display": "Fondo", "conteo": "Beneficiarios"},  # V5.1
    )
    fig.update_traces(marker_color=SAPIENCIA_COLORS["magenta_primary"], textposition="outside")
    fig.update_yaxes(title_text="Fondo")  # V5.1: sustituir "fondo_display" técnico
    fig.update_xaxes(title_text="Beneficiarios")
    _mostrar_o_vacio(_aplicar_tema(fig), agg)


def _grafico_dona_modalidad(df: pd.DataFrame) -> None:
    agg = df["Tipo_solicitud_definitiva"].value_counts().reset_index()
    agg.columns = ["modalidad", "conteo"]
    fig = px.pie(
        agg, names="modalidad", values="conteo",
        title="Distribución por Modalidad de Beneficio", hole=0.5,
        color_discrete_sequence=[SAPIENCIA_COLORS["magenta_primary"],
                                  SAPIENCIA_COLORS["magenta_dark"],
                                  SAPIENCIA_COLORS["magenta_light"]],
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    _mostrar_o_vacio(_aplicar_tema(fig), agg)


def _grafico_top5_ies(df: pd.DataFrame) -> None:
    if "IES" not in df.columns:
        st.info("📭 Columna IES no disponible")
        return
    agg = df["IES"].value_counts().head(5).reset_index()
    agg.columns = ["IES", "conteo"]
    agg = agg.sort_values("conteo", ascending=True)
    fig = px.bar(
        agg, x="conteo", y="IES", orientation="h",
        title="Top 5 IES con más Beneficiarios", text="conteo",
    )
    fig.update_traces(marker_color=SAPIENCIA_COLORS["magenta_primary"], textposition="outside")
    fig.update_yaxes(title_text="")
    fig.update_xaxes(title_text="Beneficiarios")
    _mostrar_o_vacio(_aplicar_tema(fig), agg)


def _grafico_barras_comuna_pp(df: pd.DataFrame) -> None:
    fondos_pp = ["FONDO PRESUPUESTO PARTICIPATIVO", "EXTENDIENDO FRONTERAS EDUCATIVAS PP"]
    df_pp = df[df["fondo"].isin(fondos_pp)]
    if df_pp.empty or "Comuna_de_residencia" not in df_pp.columns:
        st.info("📭 Sin datos PP para las condiciones actuales.")
        return

    agg = (
        df_pp.groupby(["Comuna_de_residencia", "grupo_estrato"], dropna=False)
        .size()
        .reset_index(name="conteo")
    )
    # Ordenar por número de comuna cuando aplique
    def _clave(v: Any) -> tuple[int, str]:
        s = str(v).strip()
        prefijo = s.split(" ")[0].strip("-")
        return (int(prefijo) if prefijo.isdigit() else 9999, s)

    orden_comunas = sorted(agg["Comuna_de_residencia"].dropna().unique().tolist(), key=_clave)

    fig = px.bar(
        agg, x="Comuna_de_residencia", y="conteo",
        color="grupo_estrato",
        title="Legalizados PP por Comuna y Estrato",
        text="conteo",  # V5.1: mostrar valor numérico en cada barra
        color_discrete_map={
            "1-3": SAPIENCIA_COLORS["magenta_primary"],
            "4-6": SAPIENCIA_COLORS["magenta_dark"],
            "N/D": SAPIENCIA_COLORS["gray_medium"],
        },
        category_orders={"Comuna_de_residencia": orden_comunas},
        barmode="group",
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(size=11, color=SAPIENCIA_COLORS["gray_dark"]),
        cliponaxis=False,
    )
    fig.update_layout(uniformtext_minsize=9, uniformtext_mode="hide")
    fig.update_xaxes(title_text="", tickangle=-45)
    fig.update_yaxes(title_text="Beneficiarios")
    _mostrar_o_vacio(_aplicar_tema(fig), agg)


def _grafico_top10_programas(df: pd.DataFrame) -> None:
    if "Programa_academico" not in df.columns:
        st.info("📭 Columna Programa_academico no disponible")
        return
    agg = df["Programa_academico"].value_counts().head(10).reset_index()
    agg.columns = ["Programa", "conteo"]
    agg = agg.sort_values("conteo", ascending=True)
    fig = px.bar(
        agg, x="conteo", y="Programa", orientation="h",
        title="Top 10 Programas Académicos", text="conteo",
    )
    fig.update_traces(marker_color=SAPIENCIA_COLORS["magenta_light"], textposition="outside")
    fig.update_yaxes(title_text="")
    fig.update_xaxes(title_text="Beneficiarios")
    _mostrar_o_vacio(_aplicar_tema(fig), agg)


def _grafico_treemap_fondo_ies(df: pd.DataFrame) -> None:
    if "IES" not in df.columns:
        st.info("📭 Columna IES no disponible")
        return
    agg = df.groupby(["fondo_display", "IES"], as_index=False).size().rename(columns={"size": "conteo"})
    if agg.empty:
        st.info("📭 Sin datos para el treemap")
        return
    fig = px.treemap(
        agg, path=["fondo_display", "IES"], values="conteo",
        title="Distribución Fondo × IES",
        color="conteo", color_continuous_scale="Purples",
    )
    _mostrar_o_vacio(_aplicar_tema(fig), agg)


def _renderizar_graficos(df: pd.DataFrame) -> None:
    st.markdown(
        f"<h3 style='color:{SAPIENCIA_COLORS['magenta_primary']};margin-top:20px;'>"
        "📊 Análisis descriptivo</h3>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        _grafico_barras_fondo(df)
    with c2:
        _grafico_dona_modalidad(df)

    c3, c4 = st.columns(2)
    with c3:
        _grafico_top5_ies(df)
    with c4:
        _grafico_top10_programas(df)

    # Ancho completo para el gráfico de comunas
    _grafico_barras_comuna_pp(df)

    _grafico_treemap_fondo_ies(df)


# ---------------------------------------------------------------------------
# Sección 6 — Tabla detallada colapsable
# ---------------------------------------------------------------------------
def _renderizar_tabla_detalle(df: pd.DataFrame) -> None:
    columnas = [
        "fondo", "Tipo_solicitud_definitiva", "IES", "Programa_academico",
        "Comuna_de_residencia", "Estrato", "Valor_matricula",
        "Valor_sostenimiento", "Pagare",
    ]
    columnas_presentes = [c for c in columnas if c in df.columns]

    with st.expander("📋 Ver detalle de registros"):
        if df.empty or not columnas_presentes:
            st.info("Sin registros para exportar.")
            return

        st.dataframe(df[columnas_presentes], use_container_width=True, height=420)

        csv = df[columnas_presentes].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"estadisticas_legalizacion_{CONVOCATORIA_ACTIVA}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# Render principal
# ---------------------------------------------------------------------------
def render_estadisticas_legalizacion() -> None:
    """Punto de entrada de la página."""
    magenta = SAPIENCIA_COLORS["magenta_primary"]

    st.markdown(
        f"<h1 style='text-align:center;color:{magenta};margin-bottom:6px;'>"
        "📊 ESTADÍSTICAS LEGALIZACIÓN</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center;color:#5f6368;margin-bottom:24px;'>"
        f"Convocatoria <strong>{CONVOCATORIA_ACTIVA}</strong> · Sapiencia -  "
        "<code>Agencia de educación postsecundaria de Medellín</code></p>",
        unsafe_allow_html=True,
    )

    # Cargar datos
    with st.spinner("📊 Cargando registros de la convocatoria..."):
        try:
            df = _cargar_giros()
        except DatabaseError as exc:
            st.error(f"❌ Error al consultar la base de datos: {exc}")
            return
        except Exception as exc:  # noqa: BLE001
            st.error(f"❌ Error inesperado: {exc}")
            return

    if df.empty:
        st.warning(f"⚠️ No hay registros para la convocatoria {CONVOCATORIA_ACTIVA}.")
        return

    # 1. Filtros
    df_filtrado = _renderizar_filtros(df)

    if df_filtrado.empty:
        st.info("📭 Ningún registro cumple los filtros seleccionados.")
        return

    st.markdown("---")

    # 2. KPIs
    _renderizar_kpis(df_filtrado)

    st.markdown("---")

    # 3. Tarjetas por modalidad
    _renderizar_modalidades(df_filtrado)

    st.markdown("---")

    # 4. Tarjetas por beneficio
    _renderizar_beneficios(df_filtrado)

    st.markdown("---")

    # 5. Gráficos
    _renderizar_graficos(df_filtrado)

    st.markdown("---")

    # 6. Tabla detallada
    _renderizar_tabla_detalle(df_filtrado)
