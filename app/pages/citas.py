"""Página de consulta de citas por documento.

Fuente de datos: vista `convocatoria_sapiencia.vw_callg_control_citas_con_historico`.

Lógica de búsqueda (Fase 3):
1. Búsqueda primaria en columna `documento`.
2. Fallback a `hist_documento` si no hay resultados o `documento` está vacío.

La vista contiene una fila por evento histórico, por lo que se deduplica
por (`fecha`, `hora_inicio`, `taquilla`) conservando la observación más
reciente (`hist_fecha_registro`).
"""
from __future__ import annotations

from datetime import datetime
from typing import Tuple

import pandas as pd
import streamlit as st

from app.config import SAPIENCIA_COLORS, settings
from app.database import DatabaseError, fetch_citas
from app.utils import (
    buscar_por_documento,
    es_documento_valido,
    escapar_html,
    format_colombia_time,
    formatear_documento,
    get_colombia_time,
)


# ---------------------------------------------------------------------------
# Carga cacheada
# ---------------------------------------------------------------------------
@st.cache_data(ttl=settings.CACHE_TTL, show_spinner=False)
def _cargar_citas() -> pd.DataFrame:
    """Trae el histórico completo de citas (cacheado por TTL)."""
    return fetch_citas()


def _consolidar_evento_mas_reciente(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce el histórico a una fila por cita conservando el evento más reciente.

    Una cita en la vista produce N filas (una por movimiento histórico).
    Para el usuario final solo importa el estado/observación más reciente.
    """
    if df.empty:
        return df

    if "hist_fecha_registro" in df.columns:
        df = df.sort_values("hist_fecha_registro", ascending=False)

    columnas_clave = [c for c in ("fecha", "hora_inicio", "taquilla") if c in df.columns]
    if columnas_clave:
        df = df.drop_duplicates(subset=columnas_clave, keep="first")

    return df


def _extraer_persona(df: pd.DataFrame) -> Tuple[str, str]:
    """Extrae el nombre y documento principal del subset de citas.

    CORRECCIÓN V4: el documento llega como float64 desde MySQL por los NaN
    de la columna; lo normalizamos con `formatear_documento` para mostrar
    "1047044130" en vez de "1047044130.0".
    """
    nombre = "No disponible"
    documento = ""

    if "nombre" in df.columns and not df["nombre"].dropna().empty:
        nombre = str(df["nombre"].dropna().iloc[0])
    elif "hist_nombre" in df.columns and not df["hist_nombre"].dropna().empty:
        nombre = str(df["hist_nombre"].dropna().iloc[0])

    if "documento" in df.columns and not df["documento"].dropna().empty:
        documento = formatear_documento(df["documento"].dropna().iloc[0])
    elif "hist_documento" in df.columns and not df["hist_documento"].dropna().empty:
        documento = formatear_documento(df["hist_documento"].dropna().iloc[0])

    return nombre, documento


def _style_estado(val: str) -> str:
    """Estilo CSS para colorear celdas según estado."""
    valor = str(val).strip().lower()
    if "asistida" in valor:
        return "background-color: #d4edda; color: #155724; font-weight: bold;"
    if "no" in valor:
        return "background-color: #f8d7da; color: #721c24;"
    return ""


def _formatear_tabla_resultados(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara las columnas a mostrar (fecha, hora, taquilla, estado, línea, observación)."""
    df_display = df.copy()

    if "fecha" in df_display.columns:
        df_display["fecha"] = pd.to_datetime(df_display["fecha"], errors="coerce").dt.strftime("%d/%m/%Y")

    if "hora_inicio" in df_display.columns:
        df_display["hora_inicio"] = pd.to_datetime(
            df_display["hora_inicio"].astype(str), format="%H:%M:%S", errors="coerce"
        ).dt.strftime("%I:%M %p")

    columnas = [c for c in ("fecha", "hora_inicio", "taquilla", "estado", "linea", "hist_observacion") if c in df_display.columns]
    df_display = df_display[columnas]

    rename_map = {
        "fecha": "Fecha",
        "hora_inicio": "Hora",
        "taquilla": "Taquilla",
        "estado": "Estado",
        "linea": "Línea",
        "hist_observacion": "Última Observación",
    }
    return df_display.rename(columns=rename_map)


# ---------------------------------------------------------------------------
# Render principal
# ---------------------------------------------------------------------------
def render_citas_page() -> None:
    """Renderiza la página de consulta de citas por documento."""
    magenta = SAPIENCIA_COLORS["magenta_primary"]
    magenta_dark = SAPIENCIA_COLORS["magenta_dark"]

    # Inicializar session_state
    st.session_state.setdefault("citas_data", None)
    st.session_state.setdefault("last_documento", "")
    st.session_state.setdefault("ultima_actualizacion_citas", get_colombia_time())

    # Títulos
    st.markdown(
        f"<h1 style='text-align: center; color: {magenta}; margin-bottom: 10px;'>"
        "📋 CONSULTA DE CITAS POR DOCUMENTO</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h3 style='text-align: center; color: #5f6368; margin-bottom: 30px;'>"
        "Sapiencia - Seguimiento de Legalización</h3>",
        unsafe_allow_html=True,
    )

    col_busqueda, col_resultados = st.columns([1, 2])

    # Panel izquierdo: búsqueda
    with col_busqueda:
        st.markdown("### 🔍 Búsqueda por Documento")

        documento = st.text_input(
            "**Número de Documento**",
            placeholder="Ej: 619630",
            help="Ingrese SOLO el número de documento (sin puntos ni espacios).",
            key="input_documento_citas",
        )

        buscar = st.button("🔍 Buscar Citas", type="primary", use_container_width=True)

        if st.button("🧹 Limpiar Búsqueda", use_container_width=True):
            st.session_state.citas_data = None
            st.session_state.last_documento = ""
            st.session_state.ultima_actualizacion_citas = get_colombia_time()
            st.rerun()

        st.markdown("---")

        last_update = format_colombia_time(st.session_state.ultima_actualizacion_citas)
        st.markdown(
            f"""
            <div style='
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid {magenta};
                margin: 15px 0 5px 0;
                text-align: center;
            '>
                <div style='font-size: 12px; color: #5f6368; font-weight: 600; margin-bottom: 3px;'>
                    📅 ÚLTIMA CONSULTA
                </div>
                <div style='font-size: 14px; color: #202124; font-weight: 700;'>
                    {last_update}
                </div>
                <div style='font-size: 11px; color: #80868b; margin-top: 8px;'>
                    Datos actualizados al presionar "Buscar Citas"
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Estadísticas cuando hay datos
        if st.session_state.citas_data is not None and not st.session_state.citas_data.empty:
            df_citas = st.session_state.citas_data
            total = len(df_citas)
            asistidas = (
                df_citas["estado"].astype(str).str.contains("Asistida", case=False, na=False).sum()
                if "estado" in df_citas.columns
                else 0
            )

            st.markdown("---")
            st.markdown("#### 📊 Estadísticas")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Total Citas", total, help="Citas únicas encontradas para el documento")
            with c2:
                st.metric("Asistidas", int(asistidas), help="Citas con estado 'Asistida'")

    # Panel derecho: resultados
    with col_resultados:
        if st.session_state.citas_data is not None:
            df_citas = st.session_state.citas_data

            if not df_citas.empty:
                nombre_principal, documento_principal = _extraer_persona(df_citas)
                # CORRECCIÓN V4: sanitizar y usar <div> en vez de <h1> para evitar
                # que el CSS global (.main h1 { color: magenta !important; }) tape
                # el texto blanco con el color del fondo.
                nombre_safe = escapar_html(nombre_principal)
                doc_safe = escapar_html(documento_principal)

                st.markdown(
                    f"<div style='background: linear-gradient(135deg, {magenta} 0%, {magenta_dark} 100%);"
                    f"padding: 26px; border-radius: 14px;"
                    f"margin-bottom: 22px; color: #FFFFFF;"
                    f"box-shadow: 0 4px 12px rgba(0,0,0,0.18);'>"
                    f"<div style='color: #FFFFFF; margin: 0 0 8px 0; font-size: 28px; font-weight: 800;"
                    f"text-shadow: 1px 1px 3px rgba(0,0,0,0.35); letter-spacing: 0.3px;'>"
                    f"👤 {nombre_safe}</div>"
                    f"<div style='color: rgba(255,255,255,0.95); margin: 0; font-size: 18px; font-weight: 500;'>"
                    f"<strong style='color: #FFFFFF;'>Documento:</strong> {doc_safe}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if st.session_state.last_documento:
                    # CORRECCIÓN V4: normalizar el documento mostrado.
                    doc_display = formatear_documento(st.session_state.last_documento) or st.session_state.last_documento
                    st.info(
                        f"🔍 Mostrando **{len(df_citas)}** cita(s) para el documento: "
                        f"**{doc_display}**"
                    )

                df_display = _formatear_tabla_resultados(df_citas)
                if df_display.empty or df_display.columns.empty:
                    st.warning("⚠️ No hay columnas reconocidas en los resultados.")
                else:
                    styled = df_display.style
                    if "Estado" in df_display.columns:
                        styled = styled.map(_style_estado, subset=["Estado"])
                    styled = styled.set_properties(**{"text-align": "center", "font-size": "14px"})

                    st.dataframe(
                        styled,
                        use_container_width=True,
                        height=min(500, len(df_display) * 40 + 60),
                    )

                    csv = df_display.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"citas_{st.session_state.last_documento}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
            else:
                if st.session_state.last_documento:
                    st.warning(
                        f"⚠️ No se encontraron citas para el documento: "
                        f"**{st.session_state.last_documento}**"
                    )
                    st.info("Verifique que el número de documento sea correcto.")
        else:
            # Estado inicial
            st.markdown(
                """
                <div style='background: #f8f9fa; padding: 80px 20px; border-radius: 15px;
                         text-align: center; margin-top: 40px; border: 2px dashed #ddd;'>
                    <div style='font-size: 64px; color: #ddd; margin-bottom: 20px;'>🔍</div>
                    <h2 style='color: #5f6368; margin-bottom: 15px;'>Consulta de Citas</h2>
                    <p style='color: #80868b; font-size: 16px; max-width: 420px; margin: 0 auto; line-height: 1.6;'>
                        Ingrese el <strong>número de documento</strong> en el panel izquierdo y<br>
                        presione <strong>"Buscar Citas"</strong> para consultar el historial.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ------------------------------------------------------------------
    # Lógica de búsqueda — se ejecuta al presionar el botón
    # ------------------------------------------------------------------
    if buscar:
        if not documento:
            st.warning("⚠️ Por favor ingrese un número de documento")
            st.stop()
        if not es_documento_valido(documento):
            st.error("❌ El documento debe contener solo números")
            st.stop()

        with st.spinner("🔍 Buscando citaciones..."):
            try:
                df_completo = _cargar_citas()
            except DatabaseError as exc:
                st.error(f"❌ Error al consultar la base de datos: {exc}")
                st.stop()
            except Exception as exc:  # noqa: BLE001 — feedback amigable al usuario
                st.error(f"❌ Error inesperado: {exc}")
                st.stop()

            df_filtrado = buscar_por_documento(df_completo, documento)
            df_consolidado = _consolidar_evento_mas_reciente(df_filtrado)

            st.session_state.citas_data = df_consolidado
            st.session_state.last_documento = documento.strip()
            st.session_state.ultima_actualizacion_citas = get_colombia_time()
            st.rerun()


if __name__ == "__main__":
    render_citas_page()
