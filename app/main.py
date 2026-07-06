"""Orquestador principal del dashboard Sapiencia.

Responsabilidades:
- Configurar la página (título, icono, layout).
- Inyectar el CSS global de la paleta Sapiencia.
- Inicializar el `session_state` (last_refresh, página activa, etc.).
- Renderizar el sidebar (navegación + logo + versión + última actualización).
- Despachar a la página correspondiente.

Notas:
- El auto-refresh se gestiona con `@st.fragment(run_every=...)` dentro de
  la página de recursos (no aquí), para evitar recargar el sidebar.
- `streamlit_app.py` solo importa `main` desde este módulo.
"""
from __future__ import annotations

import streamlit as st

from app.components.header import render_control_bar, render_header
from app.config import SAPIENCIA_COLORS, inject_global_css, settings
from app.pages import render_citas_page, render_recurso_comunas_page
from app.utils import format_colombia_time, get_colombia_time


def _init_session_state() -> None:
    """Inicializa todas las variables de `session_state` necesarias."""
    st.session_state.setdefault("last_refresh", get_colombia_time())
    st.session_state.setdefault("auto_refresh", True)
    st.session_state.setdefault("current_page", "dashboard")
    st.session_state.setdefault("citas_data", None)
    st.session_state.setdefault("last_documento", "")


def _render_sidebar() -> None:
    """Sidebar con logo, navegación, versión y última actualización."""
    magenta_primary = SAPIENCIA_COLORS["magenta_primary"]
    current_page = st.session_state.current_page

    with st.sidebar:
        # Logo / cabecera
        st.markdown(
            f"""
            <div style='text-align: center; margin: 20px 0 30px 0; padding: 12px;
                     background: rgba(255, 255, 255, 0.08); border-radius: 12px;
                     border: 1px solid rgba(255, 255, 255, 0.2);'>
                <h2 style='color: white; margin: 0; font-weight: 800; letter-spacing: 1px;'>
                    SAPIENCIA
                </h2>
                <p style='color: rgba(255, 255, 255, 0.85); font-size: 12px;
                         margin-top: 6px; font-weight: 500;'>
                    Dashboard de Fiducias
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("#### 📍 MENÚ PRINCIPAL")

        if st.button(
            "🏠 RECURSOS COMUNAS",
            use_container_width=True,
            type="primary" if current_page == "dashboard" else "secondary",
            key="btn_dashboard",
        ):
            st.session_state.current_page = "dashboard"
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        if st.button(
            "📋 CONSULTA CITAS",
            use_container_width=True,
            type="primary" if current_page == "citas" else "secondary",
            key="btn_citas",
        ):
            st.session_state.current_page = "citas"
            st.rerun()

        st.markdown("---")

        # Pie del sidebar con versión y última actualización
        last_update = format_colombia_time(st.session_state.last_refresh)
        st.markdown(
            f"""
            <div style='font-size: 11px; line-height: 1.7; padding: 12px 8px;
                     background: rgba(255, 255, 255, 0.06); border-radius: 8px;'>
                <div style='font-weight: 700; color: rgba(255, 255, 255, 0.95);'>
                    🕒 Última actualización
                </div>
                <div style='color: rgba(255, 255, 255, 0.85);'>
                    {last_update}
                </div>
                <div style='margin-top: 8px; padding-top: 6px;
                         border-top: 1px solid rgba(255, 255, 255, 0.15);
                         color: rgba(255, 255, 255, 0.75);'>
                    v{settings.APP_VERSION} | Sapiencia - DTF
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    """Punto de entrada del dashboard."""
    # Configuración de página
    st.set_page_config(
        page_title=settings.APP_TITLE,
        page_icon=settings.APP_ICON,
        layout=settings.PAGE_LAYOUT,
        initial_sidebar_state="expanded",
    )

    # CSS global con paleta Sapiencia
    inject_global_css()

    # Estado de sesión
    _init_session_state()

    # Sidebar de navegación
    _render_sidebar()

    # Contenido principal
    if st.session_state.current_page == "dashboard":
        render_header()
        auto_refresh = render_control_bar(
            st.session_state.last_refresh, st.session_state.auto_refresh
        )
        st.session_state.auto_refresh = auto_refresh
        render_recurso_comunas_page()
    else:
        render_citas_page()


if __name__ == "__main__":
    main()
