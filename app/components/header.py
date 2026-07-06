"""Encabezado y barra de control superior de la app."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from app.config import SAPIENCIA_COLORS
from app.utils import format_colombia_time, get_colombia_time


def render_header() -> None:
    """Encabezado superior con marca Sapiencia."""
    magenta_primary = SAPIENCIA_COLORS["magenta_primary"]
    magenta_dark = SAPIENCIA_COLORS["magenta_dark"]

    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {magenta_primary} 0%, {magenta_dark} 100%);
                    padding: 20px 25px;
                    border-radius: 0 0 20px 20px;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                    margin-bottom: 30px;">
            <div style="text-align: center;">
                <h1 style="color: white;
                          font-size: 36px;
                          font-weight: 900;
                          margin: 10px 0 5px 0;
                          text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.95);
                          letter-spacing: 0.5px;">
                    📊 MONITOR DE RECURSOS - SAPIENCIA
                </h1>
                <p style="color: rgba(255, 255, 255, 0.95);
                         font-size: 18px;
                         font-weight: 500;
                         margin: 5px 0 15px 0;">
                    Convocatoria 2026-2 | Agencia de Educación Postsecundaria de Medellín
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_control_bar(last_refresh: datetime, auto_refresh: bool) -> bool:
    """Barra superior con fecha de actualización y botón manual."""
    magenta_primary = SAPIENCIA_COLORS["magenta_primary"]

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        last_update = format_colombia_time(last_refresh)
        st.markdown(
            f"""
            <div style="background: #f8f9fa;
                       padding: 12px 20px;
                       border-radius: 12px;
                       border: 2px solid {magenta_primary};
                       box-shadow: 0 3px 8px rgba(171, 33, 129, 0.15);">
                <div style="color: {magenta_primary}; font-weight: 700; font-size: 14px;
                           text-align: center; margin-bottom: 5px;">
                    📅 ÚLTIMA ACTUALIZACIÓN
                </div>
                <div style="color: #202124; font-weight: 900; font-size: 18px;
                           text-align: center;">
                    {last_update}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        auto_refresh = st.checkbox(
            "🔄 **AUTO-REFRESH**",
            value=auto_refresh,
            help="Refresca los datos cada 5 minutos sin recargar toda la página",
        )

    with col3:
        if st.button("🔄 **ACTUALIZAR**", use_container_width=True, type="secondary"):
            st.session_state["last_refresh"] = get_colombia_time()
            st.cache_data.clear()
            st.rerun()

    return auto_refresh
