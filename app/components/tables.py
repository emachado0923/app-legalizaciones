"""Tablas resumen con filtros del dashboard de recursos."""
from __future__ import annotations

from typing import List, Tuple

import pandas as pd
import streamlit as st

from app.config import (
    MAPEO_FILTRO_A_FONDOS,
    OPCIONES_FILTRO_FONDOS,
    SAPIENCIA_COLORS,
    normalizar_nombre_comuna,
    obtener_cupos_aprox,
    resolver_cupos,  # V6.14
)
from app.utils import (
    etiquetar_grupo_estrato,
    format_currency,
    format_percentage,
    get_comuna_numero,
    resolver_preseleccionados,  # V8
)


def _estado_utilizacion(porcentaje: float) -> str:
    """Etiqueta de estado según porcentaje."""
    if porcentaje >= 90:
        return "POTENCIALMENTE AGOTADO"
    if porcentaje >= 70:
        return "MODERADO"
    if porcentaje >= 40:
        return "DISPONIBLE"
    return "MUY DISPONIBLE"


def _color_estado(status: str) -> str:
    """Color del badge de estado."""
    status_up = str(status).upper()
    if "POTENCIALMENTE" in status_up:
        return SAPIENCIA_COLORS["error_red"]
    if "MODERADO" in status_up:
        return SAPIENCIA_COLORS["warning_amber"]
    if "MUY DISPONIBLE" in status_up:
        return "#0b8043"
    if "DISPONIBLE" in status_up:
        return SAPIENCIA_COLORS["success_green"]
    return SAPIENCIA_COLORS["gray_medium"]


def _style_estado(val: str) -> str:
    """Estilo CSS para la celda de estado (compatible con Styler.map)."""
    color = _color_estado(val)
    return f"background-color: {color}; color: white; font-weight: bold; text-align: center;"


def _expandir_fondos_seleccionados(seleccion: List[str]) -> List[str]:
    """Traduce las opciones del multiselect a valores reales de `fuente_financiacion`."""
    fondos: List[str] = []
    for opcion in seleccion:
        fondos.extend(MAPEO_FILTRO_A_FONDOS.get(opcion, []))
    seen: set[str] = set()
    return [f for f in fondos if not (f in seen or seen.add(f))]


def _filtro_multiselect_fondos(key: str = "filtro_fondos_resumen") -> Tuple[List[str], List[str]]:
    """Renderiza el multiselect de fondos."""
    seleccion = st.multiselect(
        "🎯 **Filtrar por fondo** (puedes elegir más de uno)",
        options=OPCIONES_FILTRO_FONDOS,
        default=OPCIONES_FILTRO_FONDOS,
        help=(
            "Filtra la tabla de resumen por fuente de financiación. "
            "‘LÍNEA PREGRADO’ incluye Recurso Ordinario y Presupuesto Participativo."
        ),
        key=key,
    )
    return seleccion, _expandir_fondos_seleccionados(seleccion)


# ---------------------------------------------------------------------------
# V6.14: derivar la fuente ("RECURSO ORDINARIO" | "PRESUPUESTO PARTICIPATIVO")
# a partir del nombre del fondo (`fuente_financiacion` de la BD).
# ---------------------------------------------------------------------------
def _fuente_desde_fondo(fondo: str) -> str:
    """Extrae la fuente de financiación del nombre del fondo.

    - "EXTENDIENDO FRONTERAS - RECURSO ORDINARIO" → "RECURSO ORDINARIO"
    - "ENLAZA MUNDOS - PRESUPUESTO PARTICIPATIVO" → "PRESUPUESTO PARTICIPATIVO"
    - Fondos "puros" (sin sufijo) → devuelve el nombre completo si es una
      fuente conocida, o "" en otro caso (posgrados/MEJORES sin sufijo).
    """
    fondo_u = str(fondo or "").upper()
    if "PRESUPUESTO PARTICIPATIVO" in fondo_u:
        return "PRESUPUESTO PARTICIPATIVO"
    if "RECURSO ORDINARIO" in fondo_u:
        return "RECURSO ORDINARIO"
    if fondo_u in {"FORMACION AVANZADA", "FORMACIÓN AVANZADA", "MEJORES DEPORTISTAS"}:
        return "RECURSO ORDINARIO"  # todos los "puros" son RO por defecto
    return ""


# ---------------------------------------------------------------------------
# CORRECCIÓN V2: construcción de filas de la tabla resumen
# ---------------------------------------------------------------------------
def _key_orden_comuna(nombre: str) -> int:
    """Clave numérica para ordenar comunas (legibles + especiales)."""
    nombre_str = str(nombre)
    if " - " in nombre_str:
        prefijo = nombre_str.split(" - ", 1)[0]
        if prefijo.isdigit():
            return int(prefijo)
    # Sin número de comuna explícito (RECURSO ORDINARIO, FORMACIÓN AVANZADA, etc.)
    return 1000


def _construir_filas_resumen(df: pd.DataFrame) -> List[dict]:
    """Construye una fila por (comuna, fuente_financiacion) con métricas.

    A diferencia de la versión anterior, NO asume estratos 1-3 / 4-6 fijos:
    agrupa por (comuna, fuente_financiacion, estrato_rango) y delega la
    etiqueta del grupo al helper `etiquetar_grupo_estrato`.
    """
    if "comuna" not in df.columns or "fuente_financiacion" not in df.columns:
        return []

    filas: List[dict] = []
    # Agrupar para que cada combinación (comuna, fondo, rango) sea una fila
    cols_agrup = ["comuna", "fuente_financiacion"]
    if "estrato_rango" in df.columns:
        cols_agrup.append("estrato_rango")

    agg = (
        df.groupby(cols_agrup, dropna=False, as_index=False)
        .agg(
            usuarios=("numero_usuarios_comuna", "sum"),
            presupuesto=("presupuesto_comuna", "sum"),
            restante=("restante_presupuesto_comuna", "sum"),
        )
    )

    for _, row in agg.iterrows():
        comuna_raw = row["comuna"]
        fuente = row["fuente_financiacion"]
        estrato_rango_raw = row.get("estrato_rango") if "estrato_rango" in agg.columns else None

        nombre_normalizado = normalizar_nombre_comuna(comuna_raw)
        # Si no se mapeó a un nombre especial y no trae prefijo NN, intentamos
        # extraerlo del Nombre Comuna canónico (e.g., "01 - POPULAR").
        if str(nombre_normalizado) == str(comuna_raw):
            # Probable comuna pregrado: usar el helper de get_comuna_numero + base
            comuna_base = row.get("Comuna Base") if "Comuna Base" in df.columns else None
            if comuna_base is None and "Nombre Comuna" in df.columns:
                # buscar el primer Nombre Comuna asociado a este comuna
                match = df[df["comuna"] == comuna_raw]
                if not match.empty and "Nombre Comuna" in match.columns:
                    nombre_normalizado = str(match["Nombre Comuna"].iloc[0])

        etiqueta_estrato = etiquetar_grupo_estrato(fuente, estrato_rango_raw)

        usuarios = int(row["usuarios"] or 0)
        presupuesto = int(row["presupuesto"] or 0)
        restante = int(row["restante"] or 0)
        consumido = presupuesto - restante
        porc = (consumido / presupuesto * 100) if presupuesto > 0 else 0.0

        # V6.14: prioridad al mapa por fondo+fuente+comuna; fallback al
        # mapa legacy `CUPOS_APROXIMADOS` (pregrado LÍNEA con estrato).
        fuente_para_cupos = _fuente_desde_fondo(fuente)
        cupos = resolver_cupos(fuente, fuente_para_cupos, nombre_normalizado)
        if cupos == 0:
            cupos = obtener_cupos_aprox(nombre_normalizado, etiqueta_estrato)

        # V8: Preseleccionados por (fondo, fuente, comuna)
        preseleccionados = resolver_preseleccionados(
            fondo=fuente, fuente=fuente_para_cupos, comuna_normalizada=nombre_normalizado
        )

        filas.append({
            "Comuna": nombre_normalizado,
            "Grupo Estrato": etiqueta_estrato,
            "Usuarios Legalizados": usuarios,
            "Cupos Aprox": cupos,
            "Preseleccionados": preseleccionados,  # V8
            "Presupuesto Total": format_currency(presupuesto),
            "Presupuesto Consumido": format_currency(consumido),
            "Presupuesto Restante": format_currency(restante),
            "% Uso": format_percentage(porc),
            "Estado Utilización": _estado_utilizacion(porc),
            "_orden_comuna": _key_orden_comuna(nombre_normalizado),
            "_orden_estrato": 1 if etiqueta_estrato == "1-3" else (2 if etiqueta_estrato == "4-6" else 3),
            "_orden_fondo": str(fuente or ""),
        })

    return filas


# ---------------------------------------------------------------------------
# V6.13: helper público — el multiselect ahora se renderiza FUERA de la tabla
# para que el mismo df filtrado alimente también las tarjetas de resumen.
# ---------------------------------------------------------------------------
def render_multiselect_fondos_resumen(
    df: pd.DataFrame,
    key: str = "filtro_fondos_resumen",
) -> pd.DataFrame:
    """Muestra el multiselect de fondos y retorna el df filtrado.

    Se pensó para reutilizar el mismo df filtrado en varias secciones
    (usuarios legalizados, métricas clave, tabla resumen).
    """
    if df.empty:
        return df

    _, fondos_expandidos = _filtro_multiselect_fondos(key=key)
    if "fuente_financiacion" in df.columns and fondos_expandidos:
        return df[df["fuente_financiacion"].isin(fondos_expandidos)]
    return df


# ---------------------------------------------------------------------------
# Tabla de resumen general por comuna y estrato (con filtro multiselect)
# ---------------------------------------------------------------------------
def render_tabla_resumen_general(df: pd.DataFrame, mostrar_filtro: bool = True) -> None:
    """Renderiza la tabla de resumen general por comuna y estrato.

    Si `mostrar_filtro` es True, agrega un `st.multiselect` arriba para
    filtrar por fondo. Cuando la página ya filtró aguas arriba con
    `render_multiselect_fondos_resumen`, pasar `mostrar_filtro=False`
    y el df ya filtrado — así el multiselect no se duplica (V6.13).
    """
    if df.empty:
        st.info("📭 No hay datos para mostrar en el resumen general.")
        return

    if mostrar_filtro:
        _, fondos_expandidos = _filtro_multiselect_fondos()
        if "fuente_financiacion" in df.columns and fondos_expandidos:
            df_filtrado = df[df["fuente_financiacion"].isin(fondos_expandidos)]
        else:
            df_filtrado = df
    else:
        df_filtrado = df

    if df_filtrado.empty:
        st.info("📭 No hay registros que coincidan con el filtro seleccionado.")
        return

    filas = _construir_filas_resumen(df_filtrado)
    if not filas:
        st.info("📭 No hay registros que coincidan con el filtro seleccionado.")
        return

    summary_df = pd.DataFrame(filas).sort_values(
        ["_orden_comuna", "_orden_fondo", "_orden_estrato"]
    )
    summary_df = summary_df.drop(columns=["_orden_comuna", "_orden_fondo", "_orden_estrato"])

    styled = summary_df.style.map(_style_estado, subset=["Estado Utilización"])

    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Comuna": st.column_config.TextColumn("COMUNA", width="large"),
            "Grupo Estrato": st.column_config.TextColumn("GRUPO ESTRATO", width="small"),
            "Usuarios Legalizados": st.column_config.NumberColumn(
                "USUARIOS LEGALIZADOS", format="%d"
            ),
            "Cupos Aprox": st.column_config.NumberColumn("CUPOS APROX", format="%d"),
            "Preseleccionados": st.column_config.NumberColumn("PRESELECCIONADOS", format="%d"),  # V8
            "Presupuesto Total": st.column_config.TextColumn("PRESUPUESTO TOTAL"),
            "Presupuesto Consumido": st.column_config.TextColumn("PRESUPUESTO CONSUMIDO"),
            "Presupuesto Restante": st.column_config.TextColumn("PRESUPUESTO RESTANTE"),
            "% Uso": st.column_config.TextColumn("% USO", width="small"),
            "Estado Utilización": st.column_config.TextColumn("ESTADO UTILIZACIÓN"),
        },
    )
