# app/components/header.py
import streamlit as st
from datetime import datetime

def render_header():
    """Renderizar el encabezado del dashboard"""
    st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0; color: white;">💰 Dashboard de Fiducias - Convocatoria 2026-1</h1>
            <p style="margin: 0; color: rgba(255, 255, 255, 0.9); font-size: 1rem;">
                Sapiencia - Agencia de Educación Postsecundaria de Medellín
            </p>
        </div>
    """, unsafe_allow_html=True)

def render_control_bar(last_refresh, auto_refresh):
    """Renderizar barra de control superior"""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        last_update = last_refresh.strftime('%d/%m/%Y %I:%M %p')
        st.markdown(f"""
            <div class="time-indicator">
                <div class="dot"></div>
                <span>Última actualización: {last_update}</span>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        auto_refresh = st.checkbox(
            "🔄 Auto-refresh",
            value=auto_refresh,
            help="Actualizar cada 30 segundos"
        )
    
    with col3:
        if st.button("🔄 Actualizar", use_container_width=True):
            st.session_state.last_refresh = datetime.now()
            st.cache_data.clear()
            st.rerun()
    
    with col4:
        page_options = ["Vista General", "Detalle por Comuna"]
        current_page = st.selectbox(
            "Navegación",
            options=page_options,
            index=0,
            label_visibility="collapsed"
        )
    
    return auto_refresh, current_page