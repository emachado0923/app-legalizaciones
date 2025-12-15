# app/main.py
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
from app.pages import render_overview_page, render_detail_page

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

# En main.py, función load_custom_css(), asegúrate de incluir el CSS:
def load_custom_css():
    """Cargar CSS personalizado"""
    css = '''
    <style>
    /* TARJETA ÚNICA DE USUARIOS LEGALIZADOS */
    .single-metric-container {
        display: flex;
        justify-content: center;
        margin: 20px 0 30px 0;
    }
    
    .single-metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 20px;
        padding: 25px 40px;
        box-shadow: 0 8px 30px rgba(26, 115, 232, 0.15);
        border: 3px solid #1a73e8;
        width: 80%;
        max-width: 800px;
        text-align: center;
    }
    
    .single-metric-header {
        margin-bottom: 25px;
    }
    
    .single-metric-title {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #1a73e8 !important;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Inter', sans-serif !important;
    }
    
    .single-metric-total {
        font-size: 64px !important;
        font-weight: 900 !important;
        color: #202124 !important;
        line-height: 1;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Distribución detallada */
    .single-metric-details {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 40px;
        margin: 30px 0;
    }
    
    .detail-column {
        flex: 1;
        text-align: center;
    }
    
    .detail-label {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #5f6368 !important;
        margin-bottom: 8px;
        font-family: 'Roboto', sans-serif !important;
    }
    
    .detail-value {
        font-size: 42px !important;
        font-weight: 900 !important;
        line-height: 1;
        margin: 10px 0;
        font-family: 'Inter', sans-serif !important;
    }
    
    .detail-value.estrato-123 {
        color: #1a73e8 !important;
    }
    
    .detail-value.estrato-456 {
        color: #0d652d !important;
    }
    
    .detail-percent {
        font-size: 20px !important;
        font-weight: 700 !important;
        color: #80868b !important;
        font-family: 'Roboto', sans-serif !important;
    }
    
    .detail-separator {
        width: 2px;
        height: 80px;
        background: linear-gradient(to bottom, transparent, #dadce0, transparent);
    }
    
    /* Barra de distribución */
    .single-metric-bar {
        height: 24px;
        background-color: #eaedf2;
        border-radius: 12px;
        overflow: hidden;
        margin: 25px 0;
        border: 2px solid #dadce0;
        display: flex;
        position: relative;
    }
    
    .bar-fill {
        height: 100%;
        transition: width 1s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    .estrato-123-bar {
        background: linear-gradient(90deg, #1a73e8 0%, #4285f4 100%);
    }
    
    .estrato-456-bar {
        background: linear-gradient(90deg, #34a853 0%, #0d652d 100%);
    }
    
    .bar-label {
        color: white;
        font-size: 14px;
        font-weight: 700;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
        position: absolute;
        z-index: 2;
    }
    
    /* Footer informativo */
    .single-metric-footer {
        margin-top: 25px;
        padding-top: 20px;
        border-top: 2px solid #f0f0f0;
    }
    
    .footer-info {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 20px;
    }
    
    .footer-info span {
        font-size: 15px;
        color: #5f6368;
        font-weight: 600;
        font-family: 'Roboto', sans-serif !important;
        background: #f8f9fa;
        padding: 8px 16px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .single-metric-card {
            width: 95%;
            padding: 20px;
        }
        
        .single-metric-total {
            font-size: 48px !important;
        }
        
        .detail-value {
            font-size: 32px !important;
        }
        
        .footer-info {
            flex-direction: column;
            gap: 10px;
        }
    }
    </style>
    '''
    
    st.markdown(css, unsafe_allow_html=True)

def main():
    # Configuración de página
    st.set_page_config(
        page_title=APP_CONFIG['page_title'],
        page_icon=APP_CONFIG['page_icon'],
        layout=APP_CONFIG['layout'],
        initial_sidebar_state="expanded"
    )
    
    # Cargar CSS personalizado
    load_custom_css()
    
    # Inicializar estado de sesión
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
        st.session_state.auto_refresh = True
        st.session_state.current_page = "Vista General"
    
    # Renderizar header
    render_header()
    
    # Renderizar barra de control y obtener estado actual
    auto_refresh, current_page = render_control_bar(
        st.session_state.last_refresh,
        st.session_state.auto_refresh
    )
    
    # Actualizar estado de sesión
    st.session_state.auto_refresh = auto_refresh
    st.session_state.current_page = current_page
    
    # Obtener datos
    with st.spinner("📊 Cargando datos..."):
        df = fetch_data()
    
    # Verificar si hay datos
    if df is not None and not df.empty:
        # Mostrar página según selección
        if current_page == "Vista General":
            render_overview_page(df)
        else:  # "Detalle por Comuna"
            render_detail_page(df)
        
        # Pie de página
        st.markdown("---")
        last_update = st.session_state.last_refresh.strftime('%d/%m/%Y %I:%M %p')
        st.markdown(
            f"""
            <div style='text-align: center; color: #5f6368; font-size: 0.9rem;'>
                Sapiencia - Agencia de Educación Postsecundaria de Medellín • Dashboard v1.0 • 
                Última actualización: {last_update}
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