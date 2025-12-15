# app/main.py - VERSIÓN SIN NAVEGACIÓN
import streamlit as st
from datetime import datetime
import time
import pandas as pd
from pathlib import Path

# Importaciones internas
from app.config import APP_CONFIG
from app.database import db
from app.utils import process_comuna_data
from app.components.header import render_header, render_control_bar
from app.pages.overview import render_overview_page  # Solo importamos overview

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

# Eliminamos la función load_custom_css() ya que no se necesita más

def main():
    # Configuración de página
    st.set_page_config(
        page_title="Monitor de Recursos - Sapiencia",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"  # Ocultar sidebar
    )
    
    # Ocultar elementos de Streamlit no deseados
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ocultar sidebar completamente */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Ocultar botón de sidebar */
    button[data-testid="baseButton-header"] {
        display: none !important;
    }
    
    /* Ajustar padding superior */
    .main > div {
        padding-top: 0rem !important;
    }
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Inicializar estado de sesión
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
        st.session_state.auto_refresh = True
    
    # Renderizar header
    render_header()
    
    # Renderizar barra de control - SOLO auto_refresh
    auto_refresh = render_control_bar(
        st.session_state.last_refresh,
        st.session_state.auto_refresh
    )
    
    # Actualizar estado de sesión
    st.session_state.auto_refresh = auto_refresh
    
    # Obtener datos
    with st.spinner("📊 Cargando datos..."):
        df = fetch_data()
    
    # Verificar si hay datos
    if df is not None and not df.empty:
        # MOSTRAR SOLO LA VISTA GENERAL
        render_overview_page(df)
        
        # Pie de página simplificado
        st.markdown("---")
        last_update = st.session_state.last_refresh.strftime('%d/%m/%Y %I:%M %p')
        st.markdown(
            f"""
            <div style='text-align: center; color: #5f6368; font-size: 14px; font-weight: 500;'>
                <div style='margin-bottom: 5px;'>Sapiencia - Agencia de Educación Postsecundaria de Medellín</div>
                <div>Dashboard v1.0 • Última actualización: <strong>{last_update}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Actualización automática
        if st.session_state.auto_refresh:
            time.sleep(30)
            st.session_state.last_refresh = datetime.now()
            st.cache_data.clear()
            st.rerun()
    
    elif df is not None and df.empty:
        st.warning("⚠️ No se encontraron datos para el periodo actual. Verifique la conexión a la base de datos.")
    
    else:
        st.error("❌ Error al conectar con la base de datos. Verifique las credenciales y la conexión.")

# Para ejecución directa
if __name__ == "__main__":
    main()