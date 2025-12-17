# app/pages/overview.py - MODIFICADO
import streamlit as st
import pandas as pd
from app.utils import (
    calculate_summary_metrics, 
    get_comunas_formateadas, 
    get_comuna_numero, 
    format_comuna_con_numero,
    get_colombia_time,  # <-- NUEVA IMPORTACIÓN
    format_colombia_time  # <-- NUEVA IMPORTACIÓN
)
from app.components.cards import create_tv_cards_grid

def render_overview_page(df):
    """Renderizar página con filtro de comuna"""
    
    # Título principal
    st.markdown("<h1 style='text-align: center; color: #1a73e8; margin-bottom: 10px;'>📊 MONITOR DE RECURSOS POR COMUNA</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #5f6368; margin-bottom: 30px;'>Sapiencia - Convocatoria 2026-1</h3>", 
                unsafe_allow_html=True)
    
    # Calcular métricas
    metrics = calculate_summary_metrics(df)
    
    # Calcular usuarios por estrato
    usuarios_123 = df[df['es_123'] == True]['numero_usuarios_comuna'].sum() if 'es_123' in df.columns else 0
    usuarios_456 = df[df['es_123'] == False]['numero_usuarios_comuna'].sum() if 'es_123' in df.columns else 0
    
    # TARJETA DE USUARIOS - MEJORADA
    st.markdown("<h2 style='text-align: center;'>👥 USUARIOS LEGALIZADOS</h2>", unsafe_allow_html=True)
    
    # TOTAL EN NEGRO (diferente color)
    st.markdown(f"<h1 style='text-align: center; font-size: 72px; color: #202124; margin: 10px 0 30px 0; font-weight: 900;'>{metrics['total_usuarios']:,.0f}</h1>", 
               unsafe_allow_html=True)
    
    # Usar columnas nativas de Streamlit
    col1, col2 = st.columns(2)
    
    with col1:
        # Estratos 1-3 con etiqueta CLARA
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; 
                 border: 3px solid #1a73e8; box-shadow: 0 4px 12px rgba(26, 115, 232, 0.15);'>
            <div style='font-size: 20px; color: #1a73e8; font-weight: 700; margin-bottom: 10px;'>
                🔵 Estratos 1-3
            </div>
            <div style='font-size: 48px; color: #1a73e8; font-weight: 900;'>
                {:,}
            </div>
        </div>
        """.format(usuarios_123), unsafe_allow_html=True)
    
    with col2:
        # Estratos 4-6 con etiqueta CLARA
        st.markdown("""
        <div style='text-align: center; padding: 20px; background: white; border-radius: 15px; 
                 border: 3px solid #34a853; box-shadow: 0 4px 12px rgba(52, 168, 83, 0.15);'>
            <div style='font-size: 20px; color: #34a853; font-weight: 700; margin-bottom: 10px;'>
                🟢 Estratos 4-6
            </div>
            <div style='font-size: 48px; color: #34a853; font-weight: 900;'>
                {:,}
            </div>
        </div>
        """.format(usuarios_456), unsafe_allow_html=True)
    
    # Barra de distribución MEJORADA
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    
    # Calcular porcentajes para la barra
    total = usuarios_123 + usuarios_456
    if total > 0:
        porcentaje_123 = (usuarios_123 / total) * 100
        porcentaje_456 = (usuarios_456 / total) * 100
        
        # Etiquetas de porcentaje ARRIBA de la barra
        col_perc1, col_perc2 = st.columns(2)
        with col_perc1:
            st.markdown(f"""
            <div style='text-align: center;'>
                <div style='font-size: 18px; color: #1a73e8; font-weight: 700;'>Estratos 1-3</div>
                <div style='font-size: 24px; color: #1a73e8; font-weight: 900;'>{porcentaje_123:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_perc2:
            st.markdown(f"""
            <div style='text-align: center;'>
                <div style='font-size: 18px; color: #34a853; font-weight: 700;'>Estratos 4-6</div>
                <div style='font-size: 24px; color: #34a853; font-weight: 900;'>{porcentaje_456:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Barra visual
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        
        # Crear barra con dos columnas proporcionales
        col_bar1, col_bar2 = st.columns([porcentaje_123/100, porcentaje_456/100])
        
        with col_bar1:
            st.markdown(f"""
            <div style='background: linear-gradient(90deg, #1a73e8, #4285f4); 
                     height: 25px; border-radius: 12.5px 0 0 12.5px; 
                     display: flex; align-items: center; justify-content: center;'>
                <span style='color: white; font-weight: bold; font-size: 14px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
                    {usuarios_123:,.0f} legalizados
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        with col_bar2:
            st.markdown(f"""
            <div style='background: linear-gradient(90deg, #34a853, #0d652d); 
                     height: 25px; border-radius: 0 12.5px 12.5px 0; 
                     display: flex; align-items: center; justify-content: center;'>
                <span style='color: white; font-weight: bold; font-size: 14px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
                    {usuarios_456:,.0f} legalizados
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    # Línea separadora
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # FILTRO DE COMUNA (NUEVO) CON NÚMEROS
    st.markdown("<h2 style='text-align: center; color: #1a73e8; margin: 20px 0 20px 0;'>🏘️ RECURSOS POR COMUNA</h2>", 
                unsafe_allow_html=True)
    
    # Obtener comunas formateadas usando función centralizada
    opciones_comuna, opcion_a_nombre = get_comunas_formateadas(df)
    
    if opciones_comuna:
        # Crear contenedor para el filtro
        col_filtro1, col_filtro2, col_filtro3 = st.columns([1, 2, 1])
        
        with col_filtro2:
            # Selector de comuna con estilo mejorado
            opcion_seleccionada = st.selectbox(
                "**🔍 SELECCIONAR COMUNA**",
                options=opciones_comuna,
                index=0,
                help="Selecciona una comuna específica para ver sus recursos",
                key="filtro_comuna"
            )
            
            # Obtener el nombre real de la comuna
            comuna_seleccionada = opcion_a_nombre[opcion_seleccionada]
            
            # Mostrar indicador de qué se está mostrando
            if comuna_seleccionada == "TODAS LAS COMUNAS":
                st.markdown("""
                <div style='text-align: center; background: #e8f0fe; padding: 10px; 
                         border-radius: 10px; border: 2px solid #1a73e8; margin: 15px 0;'>
                    <span style='color: #1a73e8; font-weight: 600; font-size: 16px;'>
                        📋 Mostrando todas las comunas
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Mostrar con número y nombre
                st.markdown(f"""
                <div style='text-align: center; background: #e6f4ea; padding: 10px; 
                         border-radius: 10px; border: 2px solid #34a853; margin: 15px 0;'>
                    <span style='color: #0d652d; font-weight: 600; font-size: 16px;'>
                        📍 Mostrando recursos de: <strong>{opcion_seleccionada}</strong>
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    # Línea separadora después del filtro
    st.markdown("---")
    
    # FILTRAR DATOS SEGÚN COMUNA SELECCIONADA
    if opciones_comuna and 'opcion_seleccionada' in locals() and comuna_seleccionada != "TODAS LAS COMUNAS":
        # Filtrar por comuna específica
        # Asegurarse de que tenemos la columna Comuna Base
        if 'Comuna Base' not in df.columns and 'Nombre Comuna' in df.columns:
            df['Comuna Base'] = df['Nombre Comuna'].apply(
                lambda x: str(x).split(' - ')[1] if ' - ' in str(x) else str(x)
            )
        
        df_filtrado = df[df['Comuna Base'] == comuna_seleccionada].copy()
        
        # Verificar si hay datos para esta comuna
        if df_filtrado.empty:
            st.warning(f"⚠️ No se encontraron datos para la comuna: {comuna_seleccionada}")
            df_filtrado = df  # Mostrar todas si no hay datos
            mostrar_todas = True
        else:
            mostrar_todas = False
    else:
        # Mostrar todas las comunas
        df_filtrado = df.copy()
        mostrar_todas = True
    
    # MOSTRAR TARJETAS DE COMUNAS (filtradas o todas)
    if mostrar_todas:
        create_tv_cards_grid(df_filtrado, "Todos")
    else:
        # Para una comuna específica, mostrar solo esa
        create_tv_cards_grid(df_filtrado, "Todos")
    
    # ============================
    # PIE DE PÁGINA CON HORA COLOMBIA
    # ============================
    # Obtener la hora de Colombia usando la función de utils
    col_time = get_colombia_time()
    last_update = format_colombia_time(col_time)
    
    # Información adicional sobre lo que se está mostrando
    if opciones_comuna and 'comuna_seleccionada' in locals() and comuna_seleccionada != "TODAS LAS COMUNAS":
        info_extra = f" | Comuna: {opcion_seleccionada}"
    else:
        info_extra = " | Todas las comunas"
    
    # Crear tarjeta de última actualización
    st.markdown(f"""
    <div style='
        background-color: #f8f9fa;
        padding: 12px 20px;
        border-radius: 8px;
        border-left: 5px solid #1a73e8;
        margin: 40px auto 0 auto;
        max-width: 600px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    '>
        <div style='font-size: 14px; color: #5f6368; font-weight: 600; margin-bottom: 5px;'>
            ÚLTIMA ACTUALIZACIÓN
        </div>
        <div style='font-size: 16px; color: #202124; font-weight: 700;'>
            {last_update}
        </div>
        <div style='font-size: 12px; color: #80868b; margin-top: 8px;'>
            Sapiencia - Agencia de Educación Postsecundaria de Medellín{info_extra}
        </div>
    </div>
    """, unsafe_allow_html=True)