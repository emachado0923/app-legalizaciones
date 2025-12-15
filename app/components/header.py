# app/components/header.py - VERSIÓN SIMPLIFICADA
import streamlit as st
from datetime import datetime

def render_header():
    """Renderizar el encabezado del dashboard - SIN TÍTULO EN BLANCO"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); 
                padding: 20px 25px; 
                border-radius: 0 0 20px 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                margin-bottom: 30px;">
        <div style="text-align: center;">
            <h1 style="color: white; 
                      font-size: 36px; 
                      font-weight: 900;
                      margin: 10px 0 5px 0;
                      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                      letter-spacing: 0.5px;">
                📊 MONITOR DE RECURSOS - SAPIENCIA
            </h1>
            <p style="color: rgba(255, 255, 255, 0.95); 
                     font-size: 18px; 
                     font-weight: 500;
                     margin: 5px 0 15px 0;
                     font-family: 'Roboto', sans-serif;">
                Convocatoria 2026-1 | Agencia de Educación Postsecundaria de Medellín
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_control_bar(last_refresh, auto_refresh):
    """Renderizar barra de control superior - SIMPLIFICADA"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # FECHA DE ACTUALIZACIÓN CON MEJOR VISIBILIDAD
        last_update = last_refresh.strftime('%d/%m/%Y %I:%M %p')
        st.markdown(f"""
        <div style="background: #f8f9fa; 
                   padding: 12px 20px; 
                   border-radius: 12px; 
                   border: 2px solid #1a73e8;
                   box-shadow: 0 3px 8px rgba(26, 115, 232, 0.15);">
            <div style="color: #1a73e8; font-weight: 700; font-size: 14px; 
                       text-align: center; margin-bottom: 5px;">
                📅 ÚLTIMA ACTUALIZACIÓN
            </div>
            <div style="color: #202124; font-weight: 900; font-size: 18px;
                       text-align: center;">
                {last_update}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Checkbox de auto-refresh actualizado
        auto_refresh = st.checkbox(
            "🔄 **AUTO-REFRESH**",
            value=auto_refresh,
            help="Actualizar automáticamente cada 30 segundos"
        )
    
    with col3:
        # Botón de actualizar manual
        if st.button("🔄 **ACTUALIZAR**", use_container_width=True, type="secondary"):
            st.session_state.last_refresh = datetime.now()
            st.cache_data.clear()
            st.rerun()
    
    return auto_refresh  # Eliminamos el retorno de current_page