"""Página principal: recursos por comuna y estrato.

Fuente: tabla `convocatoria_sapiencia.callg_control_presupuesto_comuna_fidu`
filtrada por el periodo activo (`settings.CURRENT_PERIOD`).

Características:
- Total general de usuarios legalizados + tarjetas segmentadas por fondo (V2.4).
- Tabla resumen con `st.multiselect` de fondos (`OPCIONES_FILTRO_FONDOS`).
- Tarjetas dinámicas por fondo con filtros adicionales fuente/comuna (V2.2).
- Métricas superiores siempre globales (no se ven afectadas por filtros).
- Auto-refresh con `@st.fragment(run_every=...)`.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from app.components.cards import (
    agrupar_para_resumen_estrato,
    render_tarjeta_estrato_con_fiducias,
    render_tarjeta_legalizados_segmento,
    render_tarjeta_metrica,
)
from app.components.tables import render_tabla_resumen_general
from app.config import (
    CONFIGURACION_ESTRATOS_FONDOS,
    SAPIENCIA_COLORS,
    normalizar_nombre_comuna,
    settings,
)
from app.database import DatabaseError, fetch_presupuesto_comuna
from app.utils import (
    calcular_legalizados_por_segmento,
    calculate_summary_metrics,
    etiquetar_grupo_estrato,
    format_colombia_time,
    format_currency,
    format_percentage,
    get_colombia_time,
    process_comuna_data,
)


# ---------------------------------------------------------------------------
# CORRECCIÓN V2.4: Segmentos de legalizados (desglose por fondo)
# ---------------------------------------------------------------------------
SEGMENTOS_LEGALIZADOS: List[Dict[str, Any]] = [
    {
        "clave_filtro": {"fuente": "PRESUPUESTO PARTICIPATIVO", "tipo": "pregrado", "estrato_grupo": "1-3"},
        "label": "PP PREGRADO\nEstratos 1 - 3",
        "icono": "🎓",
    },
    {
        "clave_filtro": {"fuente": "PRESUPUESTO PARTICIPATIVO", "tipo": "pregrado", "estrato_grupo": "4-6"},
        "label": "PP PREGRADO\nEstratos 4 - 6",
        "icono": "🎓",
    },
    {
        "clave_filtro": {"fuente": "RECURSO ORDINARIO", "tipo": "pregrado"},
        "label": "PREGRADO\nRecurso Ordinario",
        "icono": "📚",
    },
    {
        "clave_filtro": {"fuente": "PRESUPUESTO PARTICIPATIVO", "fondo": "EXTENDIENDO FRONTERAS"},
        "label": "EXTENDIENDO\nFRONTERAS PP",
        "icono": "🌎",
    },
    {
        "clave_filtro": {"fuente": "RECURSO ORDINARIO", "fondo": "EXTENDIENDO FRONTERAS"},
        "label": "EXTENDIENDO\nFRONTERAS RO",
        "icono": "🌎",
    },
    {"clave_filtro": {"fondo": "FORMACION AVANZADA"}, "label": "FORMACIÓN\nAVANZADA", "icono": "🏆"},
    {"clave_filtro": {"fondo": "MEJORES DEPORTISTAS"}, "label": "MEJORES\nDEPORTISTAS", "icono": "⚽"},
]


# ---------------------------------------------------------------------------
# Carga de datos cacheada (NO cachea conexiones, solo DataFrames)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=settings.CACHE_TTL, show_spinner=False)
def _cargar_presupuesto() -> pd.DataFrame:
    """Trae el presupuesto del periodo activo y enriquece columnas derivadas."""
    df = fetch_presupuesto_comuna(settings.CURRENT_PERIOD)
    return process_comuna_data(df)


# ---------------------------------------------------------------------------
# Métricas clave (siempre globales)
# ---------------------------------------------------------------------------
def _renderizar_metricas_clave(df: pd.DataFrame) -> None:
    """Métricas superiores: totales globales (NO se filtran por fondo)."""
    metrics = calculate_summary_metrics(df)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_tarjeta_metrica(
            titulo="PRESUPUESTO TOTAL",
            valor=format_currency(metrics["total_presupuesto"]),
            descripcion="Monto total asignado",
            color_borde=SAPIENCIA_COLORS["magenta_primary"],
            icono="💰",
        )

    with col2:
        render_tarjeta_metrica(
            titulo="PRESUPUESTO OTORGADO",
            valor=format_currency(metrics["total_consumido"]),
            descripcion="Monto ya asignado",
            color_borde=SAPIENCIA_COLORS["error_red"],
            icono="📈",
        )

    with col3:
        render_tarjeta_metrica(
            titulo="PRESUPUESTO RESTANTE",
            valor=format_currency(metrics["total_restante"]),
            descripcion="Monto disponible",
            color_borde=SAPIENCIA_COLORS["success_green"],
            icono="📉",
        )

    with col4:
        porc = metrics["porcentaje_utilizacion"]
        if porc >= 90:
            color, estado, icono = SAPIENCIA_COLORS["error_red"], "Crítico", "⚠️"
        elif porc >= 70:
            color, estado, icono = SAPIENCIA_COLORS["warning_amber"], "Moderado", "📊"
        elif porc >= 40:
            color, estado, icono = SAPIENCIA_COLORS["success_green"], "Disponible", "✅"
        else:
            color, estado, icono = "#0b8043", "Muy disponible", "🟢"

        render_tarjeta_metrica(
            titulo="% PRESUPUESTO UTILIZADO",
            valor=format_percentage(porc),
            descripcion=f"Estado: {estado}",
            color_borde=color,
            icono=icono,
        )


# ---------------------------------------------------------------------------
# CORRECCIÓN V2.4: total + tarjetas segmentadas por fondo
# ---------------------------------------------------------------------------
def _renderizar_resumen_usuarios(df: pd.DataFrame) -> None:
    """Total de usuarios legalizados + tarjetas por segmento (1 por fondo)."""
    magenta = SAPIENCIA_COLORS["magenta_primary"]

    total = (
        int(df["numero_usuarios_comuna"].fillna(0).sum())
        if "numero_usuarios_comuna" in df.columns
        else 0
    )

    st.markdown(
        f"<h2 style='text-align: center; color: {magenta};'>👥 USUARIOS LEGALIZADOS</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<h1 style='text-align: center; font-size: 64px; color: {SAPIENCIA_COLORS['gray_dark']}; "
        f"margin: 8px 0 24px 0; font-weight: 900;'>{total:,}</h1>",
        unsafe_allow_html=True,
    )

    # Cuadrícula de 4 columnas para hasta N tarjetas
    n_cols = 4
    cols = st.columns(n_cols)
    for idx, segmento in enumerate(SEGMENTOS_LEGALIZADOS):
        valor = calcular_legalizados_por_segmento(df, segmento["clave_filtro"])
        with cols[idx % n_cols]:
            render_tarjeta_legalizados_segmento(
                titulo=segmento["label"],
                valor=valor,
                icono=segmento.get("icono", "🎓"),
            )


# ---------------------------------------------------------------------------
# CORRECCIÓN V2.2: dropdowns para filtrar tarjetas por fondo y comuna
# ---------------------------------------------------------------------------
def _opciones_comuna_para_dropdown(df: pd.DataFrame) -> tuple[list[str], dict[str, Any]]:
    """Devuelve (etiquetas_display ordenadas, mapa_display_a_codigo).

    Resuelve la etiqueta humana en este orden:
    1. `normalizar_nombre_comuna(codigo)` para códigos especiales (EFE, FA, MD).
    2. `Nombre Comuna` derivado por `process_comuna_data` (pregrado PP y RO).
    3. Código en bruto como último recurso.
    """
    if "comuna" not in df.columns:
        return [], {}

    display_a_codigo: dict[str, Any] = {}
    items: list[tuple[int, str]] = []  # (orden, etiqueta)

    for codigo in df["comuna"].dropna().unique().tolist():
        # 1) Mapeo especial
        etiqueta = normalizar_nombre_comuna(codigo)
        # 2) Si no hubo mapeo especial, usar Nombre Comuna
        if str(etiqueta) == str(codigo) and "Nombre Comuna" in df.columns:
            fila = df[df["comuna"] == codigo]["Nombre Comuna"]
            if not fila.empty:
                etiqueta = str(fila.iloc[0])
        # Resolver duplicados (varios códigos pueden mapear al mismo nombre)
        clave_display = etiqueta
        sufijo = 2
        while clave_display in display_a_codigo:
            clave_display = f"{etiqueta} ({codigo})"
            sufijo += 1
        display_a_codigo[clave_display] = codigo

        # Clave de orden numérica si la etiqueta empieza con "NN - "
        try:
            prefijo = clave_display.split(" - ", 1)[0]
            orden = int(prefijo) if prefijo.isdigit() else 9999
        except (ValueError, IndexError):
            orden = 9999
        items.append((orden, clave_display))

    items.sort(key=lambda x: (x[0], x[1]))
    etiquetas = [e for _, e in items]
    return etiquetas, display_a_codigo


def _seccion_tarjetas_por_fondo(df: pd.DataFrame) -> None:
    """Sección de tarjetas dinámicas con filtros fuente_financiacion + comuna."""
    magenta = SAPIENCIA_COLORS["magenta_primary"]

    st.markdown(
        f"<h2 style='text-align: center; color: {magenta}; margin: 16px 0 16px 0;'>"
        "🏘️ RECURSOS POR FONDO Y ESTRATO</h2>",
        unsafe_allow_html=True,
    )

    if df.empty or "fuente_financiacion" not in df.columns:
        st.info("📭 No hay datos para mostrar.")
        return

    # --- Filtros ---
    fuentes_disponibles = sorted(df["fuente_financiacion"].dropna().unique().tolist())
    fuentes_configuradas = [f for f in fuentes_disponibles if f in CONFIGURACION_ESTRATOS_FONDOS]

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        fuente_seleccionada = st.selectbox(
            "Fuente de financiación",
            options=["Todas"] + fuentes_configuradas,
            key="filtro_fuente_tarjetas",
            help="Filtra las tarjetas mostradas por fuente de financiación.",
        )

    with col_f2:
        df_para_comunas = (
            df if fuente_seleccionada == "Todas"
            else df[df["fuente_financiacion"] == fuente_seleccionada]
        )
        etiquetas_comuna, mapa_comuna = _opciones_comuna_para_dropdown(df_para_comunas)
        comuna_display = st.selectbox(
            "Comuna",
            options=["Todas"] + etiquetas_comuna,
            key="filtro_comuna_tarjetas",
            help="Filtra las tarjetas a una comuna específica.",
        )
        comuna_codigo = mapa_comuna.get(comuna_display, "Todas") if comuna_display != "Todas" else "Todas"

    # --- Aplicar filtros ---
    df_tarjetas = df.copy()
    if fuente_seleccionada != "Todas":
        df_tarjetas = df_tarjetas[df_tarjetas["fuente_financiacion"] == fuente_seleccionada]
    if comuna_codigo != "Todas":
        df_tarjetas = df_tarjetas[df_tarjetas["comuna"].astype(str) == str(comuna_codigo)]

    if df_tarjetas.empty:
        st.info("📭 No hay datos para la combinación seleccionada.")
        return

    # --- Leyenda (CORRECCIÓN V3: 5 estados) ---
    with st.expander("📋 LEYENDA - ESTADOS DE UTILIZACIÓN", expanded=False):
        cols = st.columns(5)
        estados = [
            ("MUY DISPONIBLE", "< 30% usado", "#2E7D32", "#d5e8d9"),
            ("DISPONIBLE", "30-59% usado", "#558B2F", "#e6f4ea"),
            ("MODERADO", "60-79% usado", "#F57F17", "#fef7e0"),
            ("ALTO USO", "80-94% usado", "#E65100", "#fce4d4"),
            ("CRÍTICO", ">= 95% usado", "#C62828", "#fce8e6"),
        ]
        for idx, (nombre, desc, color, bg) in enumerate(estados):
            with cols[idx]:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 10px; background: {bg};
                             border-radius: 8px; border: 2px solid {color};">
                        <div style="font-weight: 900; color: {color}; font-size: 13px;">{nombre}</div>
                        <div style="color: #666; font-size: 11px;">{desc}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- Render por (fondo, comuna, estrato_rango) [CORRECCIÓN V3] ---
    fondos_a_mostrar = sorted(df_tarjetas["fuente_financiacion"].dropna().unique().tolist())
    fondos_a_mostrar = [f for f in fondos_a_mostrar if f in CONFIGURACION_ESTRATOS_FONDOS]
    if not fondos_a_mostrar:
        st.info("📭 Ningún fondo coincide con la configuración activa.")
        return

    color_header_fondo = SAPIENCIA_COLORS["magenta_dark"]

    for fondo in fondos_a_mostrar:
        df_fondo = df_tarjetas[df_tarjetas["fuente_financiacion"] == fondo]
        if df_fondo.empty:
            continue

        st.subheader(f"📦 {fondo}")

        # Ordenar comunas dentro del fondo por su número (si es numérico)
        codigos_comuna = df_fondo["comuna"].dropna().unique().tolist()

        def _orden_codigo(codigo: Any) -> tuple[int, str]:
            etiqueta = normalizar_nombre_comuna(codigo)
            if str(etiqueta) == str(codigo) and "Nombre Comuna" in df_fondo.columns:
                fila = df_fondo[df_fondo["comuna"] == codigo]["Nombre Comuna"]
                if not fila.empty:
                    etiqueta = str(fila.iloc[0])
            prefijo = str(etiqueta).split(" - ", 1)[0]
            return (int(prefijo) if prefijo.isdigit() else 9999, str(etiqueta))

        codigos_comuna_ordenados = sorted(codigos_comuna, key=_orden_codigo)

        primera_comuna = True
        for codigo_comuna in codigos_comuna_ordenados:
            if not primera_comuna:
                st.divider()
            primera_comuna = False

            df_comuna = df_fondo[df_fondo["comuna"] == codigo_comuna]

            # Etiqueta humana para la comuna
            etiqueta = normalizar_nombre_comuna(codigo_comuna)
            if str(etiqueta) == str(codigo_comuna) and "Nombre Comuna" in df_comuna.columns:
                etiqueta = str(df_comuna["Nombre Comuna"].iloc[0])

            # Separar número (si hay) y nombre
            if " - " in str(etiqueta):
                numero_str, nombre_str = str(etiqueta).split(" - ", 1)
                if not numero_str.isdigit():
                    numero_str, nombre_str = "", str(etiqueta)
            else:
                numero_str, nombre_str = "", str(etiqueta)

            # Estratos disponibles para esta comuna en este fondo
            if "estrato_rango" in df_comuna.columns:
                rangos = df_comuna["estrato_rango"].unique().tolist()
            else:
                rangos = [None]

            # Orden: 1-3 primero, luego 4-6, luego None (posgrados / RO)
            def _orden_rango(r: Any) -> int:
                if r == "1-3":
                    return 0
                if r == "4-6":
                    return 1
                return 2

            rangos_ordenados = sorted(rangos, key=_orden_rango)

            for estrato_rango_valor in rangos_ordenados:
                datos = agrupar_para_resumen_estrato(
                    df_comuna,
                    {
                        "fondo": fondo,
                        "comuna": codigo_comuna,
                        "estrato_rango": estrato_rango_valor,
                    },
                )
                if datos["presupuesto_total"] == 0 and datos["legalizados"] == 0 and not datos["fiducias"]:
                    continue

                etiqueta_estrato = etiquetar_grupo_estrato(fondo, estrato_rango_valor)
                render_tarjeta_estrato_con_fiducias(
                    nombre_comuna=nombre_str,
                    numero_comuna=numero_str,
                    grupo_estrato=etiqueta_estrato,
                    datos=datos,
                    color_header=color_header_fondo,
                )


# ---------------------------------------------------------------------------
# Fragmento auto-refrescante
# ---------------------------------------------------------------------------
@st.fragment(run_every=settings.CACHE_TTL)
def _fragmento_datos_en_vivo() -> None:
    """Sección que se refresca cada `CACHE_TTL` segundos sin recargar toda la página."""
    magenta = SAPIENCIA_COLORS["magenta_primary"]

    try:
        df = _cargar_presupuesto()
    except DatabaseError as exc:
        st.error(f"❌ Error al consultar la base de datos: {exc}")
        return
    except Exception as exc:  # noqa: BLE001
        st.error(f"❌ Error inesperado al cargar datos: {exc}")
        return

    if df.empty:
        st.warning("⚠️ No se encontraron datos para el periodo actual.")
        return

    # 1. USUARIOS LEGALIZADOS — total + tarjetas segmentadas (CORRECCIÓN V2.4)
    _renderizar_resumen_usuarios(df)
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # 2. TABLA RESUMEN GENERAL POR COMUNA Y ESTRATO (CORRECCIÓN V2.1)
    st.markdown(
        f"<h2 style='text-align: center; color: {magenta}; margin: 16px 0 20px 0;'>"
        "📋 RESUMEN GENERAL POR COMUNA Y ESTRATO</h2>",
        unsafe_allow_html=True,
    )
    render_tabla_resumen_general(df, mostrar_filtro=True)

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # 3. MÉTRICAS CLAVE (siempre globales)
    st.markdown(
        f"<h2 style='text-align: center; color: {magenta}; margin: 16px 0 20px 0;'>"
        "📊 RESUMEN GENERAL DE RECURSOS</h2>",
        unsafe_allow_html=True,
    )
    _renderizar_metricas_clave(df)

    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.markdown("---")

    # 4. TARJETAS DINÁMICAS POR FONDO con filtros fuente + comuna (CORRECCIÓN V2.2)
    _seccion_tarjetas_por_fondo(df)

    # 5. Pie de página
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    last_update = format_colombia_time(get_colombia_time())
    st.markdown(
        f"""
        <div style='
            background-color: #f8f9fa;
            padding: 12px 20px;
            border-radius: 8px;
            border-left: 5px solid {magenta};
            margin: 24px auto 0 auto;
            max-width: 620px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        '>
            <div style='font-size: 14px; color: #5f6368; font-weight: 600; margin-bottom: 5px;'>
                ÚLTIMA ACTUALIZACIÓN
            </div>
            <div style='font-size: 16px; color: {SAPIENCIA_COLORS['gray_dark']}; font-weight: 700;'>
                {last_update}
            </div>
            <div style='font-size: 12px; color: #80868b; margin-top: 8px;'>
                Sapiencia - Agencia de Educación Postsecundaria de Medellín
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recurso_comunas_page() -> None:
    """Punto de entrada de la página de recursos por comuna."""
    _fragmento_datos_en_vivo()
