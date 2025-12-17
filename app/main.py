# app/main.py - VERSIÓN CON INICIALIZACIÓN COMPLETA
import streamlit as st
import time
import pandas as pd
from pathlib import Path
from app.config import APP_CONFIG
from app.database import db
from app.utils import process_comuna_data, get_colombia_time
from app.components.header import render_header, render_control_bar
from app.pages.overview import render_overview_page
from app.pages.citas import render_citas_page

@st.cache_data(ttl=APP_CONFIG['cache_ttl'])
def fetch_data():
    """Obtener datos de la base de datos"""
    try:
        results = db.fetch_all_data(APP_CONFIG['table_name'], APP_CONFIG['current_period'])
        
        if results:
            df = pd.DataFrame(results)
            df = process_comuna_data(df)
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

def main():
    # Configuración de página
    st.set_page_config(
        page_title="Monitor de Recursos - Sapiencia",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # ============================================
    # INICIALIZACIÓN COMPLETA DE SESSION_STATE
    # ============================================
    # Siempre inicializar TODAS las variables al inicio
    
    # 1. Variables para el dashboard
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = get_colombia_time()
    
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    
    # 2. Variables de navegación
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"  # "dashboard" o "citas"
    
    # 3. Variables para la página de citas
    if 'citas_data' not in st.session_state:
        st.session_state.citas_data = None
    
    if 'last_documento' not in st.session_state:
        st.session_state.last_documento = ""
    
    # ============================
    # SIDEBAR - MENÚ SIMPLIFICADO
    # ============================
    with st.sidebar:
        # Logo y título mínimo
        st.markdown("""
        <div style='text-align: center; margin: 20px 0 40px 0;'>
            <h2 style='color: #1a73e8; margin: 0;'>LEGALIZACIONES</h2>
            <p style='color: #5f6368; font-size: 12px; margin-top: 5px;'>Recursos y citas</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menú de navegación VERTICAL
        st.markdown("#### 📍 MENÚ PRINCIPAL")
        
        # Obtener la página actual para determinar qué botón está activo
        current_page = st.session_state.current_page
        
        # Botón Dashboard
        if st.button(
            "🏠 RECURSOS COMUNAS", 
            use_container_width=True,
            type="primary" if current_page == "dashboard" else "secondary",
            key="btn_dashboard"
        ):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Botón Citas
        if st.button(
            "📋 CONSULTA CITAS", 
            use_container_width=True,
            type="primary" if current_page == "citas" else "secondary",
            key="btn_citas"
        ):
            st.session_state.current_page = "citas"
            st.rerun()
        
        st.markdown("---")
        
        # Información mínima
        last_update = st.session_state.last_refresh.strftime('%d/%m/%Y %I:%M %p')
        st.caption(f"🕒 {last_update}")
        st.caption("v1.2.0 | Sapiencia - DTF")
    
    # ============================
    # CONTENIDO PRINCIPAL
    # ============================
    current_page = st.session_state.current_page  # Usar variable local
    
    if current_page == "dashboard":
        # Renderizar header
        render_header()
        
        # Renderizar barra de control con auto-refresh
        auto_refresh = render_control_bar(
            st.session_state.last_refresh,
            st.session_state.auto_refresh
        )
        
        # Actualizar estado de auto_refresh si cambió
        if auto_refresh != st.session_state.auto_refresh:
            st.session_state.auto_refresh = auto_refresh
        
        # Obtener datos
        with st.spinner("📊 Cargando datos del dashboard..."):
            df = fetch_data()
        
        if df is not None and not df.empty:
            render_overview_page(df)
            
            # Auto-refresh solo en dashboard
            if st.session_state.auto_refresh:
                time.sleep(30)
                st.session_state.last_refresh = get_colombia_time()
                st.cache_data.clear()
                st.rerun()
        
        elif df is not None and df.empty:
            st.warning("⚠️ No se encontraron datos para el periodo actual.")
        else:
            st.error("❌ Error al conectar con la base de datos.")
    
    elif current_page == "citas":
        # Renderizar página de citas
        render_citas_page()

if __name__ == "__main__":
    main()