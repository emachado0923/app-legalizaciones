# app/pages/overview.py - VERSIÓN CON MÉTRICAS EN POSICIÓN CORRECTA
import streamlit as st
import pandas as pd
from app.utils import (
    calculate_summary_metrics, 
    get_comunas_formateadas, 
    get_comuna_numero, 
    format_comuna_con_numero,
    get_colombia_time,
    format_colombia_time
)
from app.components.cards import create_tv_cards_grid

CUPOS_APROXIMADOS = {
    # Formato: "NUMERO - COMUNA": {"1-3": cantidad, "4-6": cantidad}
    "01 - POPULAR": {"1-3": 16, "4-6": "N.A"},
    "02 - SANTA CRUZ": {"1-3": 19, "4-6": "N.A"},
    "03 - MANRIQUE": {"1-3": 17, "4-6": "N.A"},
    "04 - ARANJUEZ": {"1-3": 20, "4-6": "N.A"},
    "05 - CASTILLA": {"1-3": 18, "4-6": "N.A"},
    "06 - DOCE DE OCTUBRE": {"1-3": 15, "4-6": "N.A"},
    "07 - ROBLEDO": {"1-3": 23, "4-6": 6},
    "08 - VILLA HERMOSA": {"1-3": 16, "4-6": 8},
    "09 - BUENOS AIRES": {"1-3": 19, "4-6": 5},
    "10 - LA CANDELARIA": {"1-3": 14, "4-6": 9},
    "11 - LAURELES/ESTADIO": {"1-3": 2, "4-6": 12},
    "12 - LA AMERICA": {"1-3": 9, "4-6": 9},
    "13 - SAN JAVIER": {"1-3": 23, "4-6": "N.A"},
    "14 - POBLADO": {"1-3": 12, "4-6": 17},
    "15 - GUAYABAL": {"1-3": 11, "4-6": 8},
    "16 - BELEN": {"1-3": 29, "4-6": 12},
    "50 - SAN SEBASTIAN DE PALMITAS": {"1-3": 14, "4-6": "N.A"},
    "60 - SAN CRISTOBAL": {"1-3": 18, "4-6": "N.A"},
    "70 - ALTAVISTA": {"1-3": 8, "4-6": "N.A"},
    "80 - SAN ANTONIO DE PRADO": {"1-3": 38, "4-6": "N.A"},
    "90 - SANTA ELENA": {"1-3": 17, "4-6": 2},
    "00 - RECURSO ORDINARIO": {"1-4": 301},
    "00 - MEJORES DEPORTISTAS": { "N.A":  "N.A"}
}

def _get_cupos_aprox(comuna_con_numero, grupo_estrato):
    """
    Obtener cupos aproximados del mapeo
    Args:
        comuna_con_numero: "01 - POPULAR"
        grupo_estrato: "1-3" o "4-6"
    """
    # Limpiar el string si tiene texto adicional
    clave = comuna_con_numero
    if " (Estrato" in clave:
        clave = clave.split(" (Estrato")[0].strip()
    
    if clave in CUPOS_APROXIMADOS and grupo_estrato in CUPOS_APROXIMADOS[clave]:
        return CUPOS_APROXIMADOS[clave][grupo_estrato]
    return 0

def render_overview_page(df):
    """Renderizar página con filtro de comuna"""
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
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
    
    # ============================
    # TABLA RESUMEN GLOBAL
    # ============================
    st.markdown("<h2 style='text-align: center; color: #1a73e8; margin: 20px 0 30px 0;'>📋 RESUMEN GENERAL POR COMUNA Y ESTRATO</h2>", 
                unsafe_allow_html=True)
    
    # Crear tabla resumen con todas las columnas solicitadas
    if not df.empty and 'es_123' in df.columns:
        summary_data = []
        
        # Primero agrupar por comuna
        comunas_base = df['Comuna Base'].unique() if 'Comuna Base' in df.columns else []
        
        for comuna in comunas_base:
            df_comuna = df[df['Comuna Base'] == comuna]
            
            # Obtener número de comuna
            numero_comuna = get_comuna_numero(comuna)
            
            # Datos para estrato 1-3
            df_123 = df_comuna[df_comuna['es_123'] == True]
            if not df_123.empty:
                usuarios_123_comuna = int(df_123['numero_usuarios_comuna'].sum())
                presupuesto_total_123 = df_123['presupuesto_comuna'].sum()
                presupuesto_consumido_123 = presupuesto_total_123 - df_123['restante_presupuesto_comuna'].sum()
                presupuesto_restante_123 = df_123['restante_presupuesto_comuna'].sum()
                
                # Calcular porcentaje
                porcentaje_123 = (presupuesto_consumido_123 / presupuesto_total_123 * 100) if presupuesto_total_123 > 0 else 0
                
                # Determinar estado usando función existente (de utils.py o cards.py)
                estado_123 = _get_estado_utilizacion(porcentaje_123)

                comuna_con_numero = f"{numero_comuna} - {comuna}"
                cupos_123 = _get_cupos_aprox(comuna_con_numero, '1-3')
                
                summary_data.append({
                    'Comuna': f"{numero_comuna} - {comuna}",
                    'Grupo Estrato': '1-3',
                    'Usuarios Legalizados': usuarios_123_comuna,
                    'Cupos Aprox': cupos_123,
                    'Presupuesto Total': presupuesto_total_123,
                    'Presupuesto Consumido': presupuesto_consumido_123,
                    'Presupuesto Restante': presupuesto_restante_123,
                    '% Uso': porcentaje_123,
                    'Estado Utilización': estado_123
                })
            
            # Datos para estrato 4-6
            df_456 = df_comuna[df_comuna['es_123'] == False]
            if not df_456.empty:
                usuarios_456_comuna = int(df_456['numero_usuarios_comuna'].sum())
                presupuesto_total_456 = df_456['presupuesto_comuna'].sum()
                presupuesto_consumido_456 = presupuesto_total_456 - df_456['restante_presupuesto_comuna'].sum()
                presupuesto_restante_456 = df_456['restante_presupuesto_comuna'].sum()
                
                # Calcular porcentaje
                porcentaje_456 = (presupuesto_consumido_456 / presupuesto_total_456 * 100) if presupuesto_total_456 > 0 else 0
                
                # Determinar estado usando función existente
                estado_456 = _get_estado_utilizacion(porcentaje_456)

                comuna_con_numero = f"{numero_comuna} - {comuna}"
                cupos_456 = _get_cupos_aprox(comuna_con_numero, '4-6')
                
                summary_data.append({
                    'Comuna': f"{numero_comuna} - {comuna}",
                    'Grupo Estrato': '4-6',
                    'Usuarios Legalizados': usuarios_456_comuna,
                    'Cupos Aprox': cupos_456,
                    'Presupuesto Total': presupuesto_total_456,
                    'Presupuesto Consumido': presupuesto_consumido_456,
                    'Presupuesto Restante': presupuesto_restante_456,
                    '% Uso': porcentaje_456,
                    'Estado Utilización': estado_456
                })
        
        # Crear DataFrame
        summary_df = pd.DataFrame(summary_data)
        
        # Ordenar por número de comuna
        if not summary_df.empty:
            summary_df['Numero'] = summary_df['Comuna'].apply(
                lambda x: int(x.split(' - ')[0]) if x.split(' - ')[0].isdigit() else 999
            )
            summary_df = summary_df.sort_values(['Numero', 'Grupo Estrato'])
            summary_df = summary_df.drop('Numero', axis=1)
            
            # Formatear valores para visualización
            summary_df_display = summary_df.copy()
            
            # Formatear valores monetarios COMPLETOS (sin B, M, K)
            for col in ['Presupuesto Total', 'Presupuesto Consumido', 'Presupuesto Restante']:
                if col in summary_df_display.columns:
                    summary_df_display[col] = summary_df_display[col].apply(lambda x: f"${x:,.0f}")
            
            # Formatear porcentaje
            if '% Uso' in summary_df_display.columns:
                summary_df_display['% Uso'] = summary_df_display['% Uso'].apply(lambda x: f"{x:.1f}%")
            
            # Aplicar estilos a la columna Estado Utilización
            styled_df = summary_df_display.style.apply(
                lambda x: [_apply_color_to_status(val) for val in x], 
                subset=['Estado Utilización']
            )
            
            # Mostrar tabla con st.dataframe con colores
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Comuna': st.column_config.TextColumn('COMUNA', width='large'),
                    'Grupo Estrato': st.column_config.TextColumn('GRUPO ESTRATO', width='small'),
                    'Usuarios Legalizados': st.column_config.NumberColumn('USUARIOS LEGALIZADOS', format='%d'),
                    'Cupos Aprox': st.column_config.NumberColumn('CUPOS APROX', format='%d'),
                    'Presupuesto Total': st.column_config.TextColumn('PRESUPUESTO TOTAL'),
                    'Presupuesto Consumido': st.column_config.TextColumn('PRESUPUESTO CONSUMIDO'),
                    'Presupuesto Restante': st.column_config.TextColumn('PRESUPUESTO RESTANTE'),
                    '% Uso': st.column_config.TextColumn('% USO', width='small'),
                    'Estado Utilización': st.column_config.TextColumn('ESTADO UTILIZACIÓN')
                }
            )
    
    # Línea separadora
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ============================
    # MÉTRICAS CLAVE - DESPUÉS DE LA TABLA
    # ============================
    st.markdown("<h2 style='text-align: center; color: #1a73e8; margin: 20px 0 30px 0;'>📊 RESUMEN GENERAL DE RECURSOS</h2>", 
                unsafe_allow_html=True)
    
    # Calcular métricas generales
    if 'presupuesto_comuna' in df.columns and 'restante_presupuesto_comuna' in df.columns:
        presupuesto_total = df['presupuesto_comuna'].sum()
        presupuesto_consumido = presupuesto_total - df['restante_presupuesto_comuna'].sum()
        presupuesto_restante = df['restante_presupuesto_comuna'].sum()
    else:
        presupuesto_total = 0
        presupuesto_consumido = 0
        presupuesto_restante = 0
    
    total_usuarios = df['numero_usuarios_comuna'].sum() if 'numero_usuarios_comuna' in df.columns else 0
    
    # Crear 4 columnas para las métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # PRESUPUESTO TOTAL
        st.markdown(f"""
        <div style='
            background: white;
            border-radius: 15px;
            padding: 25px 15px;
            text-align: center;
            border: 2px solid #1a73e8;
            box-shadow: 0 4px 12px rgba(26, 115, 232, 0.1);
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <div style='
                font-size: 16px;
                color: #5f6368;
                font-weight: 700;
                margin-bottom: 15px;
            '>
                💰 PRESUPUESTO TOTAL
            </div>
            <div style='
                font-size: 28px;
                color: #1a73e8;
                font-weight: 900;
                line-height: 1.2;
                word-break: break-word;
            '>
                ${presupuesto_total:,.0f}
            </div>
            <div style='
                font-size: 14px;
                color: #80868b;
                margin-top: 12px;
            '>
                Monto total asignado
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # PRESUPUESTO OTORGADO (CONSUMIDO)
        st.markdown(f"""
        <div style='
            background: white;
            border-radius: 15px;
            padding: 25px 15px;
            text-align: center;
            border: 2px solid #ea4335;
            box-shadow: 0 4px 12px rgba(234, 67, 53, 0.1);
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <div style='
                font-size: 16px;
                color: #5f6368;
                font-weight: 700;
                margin-bottom: 15px;
            '>
                📈 PRESUPUESTO OTORGADO
            </div>
            <div style='
                font-size: 28px;
                color: #ea4335;
                font-weight: 900;
                line-height: 1.2;
                word-break: break-word;
            '>
                ${presupuesto_consumido:,.0f}
            </div>
            <div style='
                font-size: 14px;
                color: #80868b;
                margin-top: 12px;
            '>
                Monto ya asignado
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # PRESUPUESTO RESTANTE
        st.markdown(f"""
        <div style='
            background: white;
            border-radius: 15px;
            padding: 25px 15px;
            text-align: center;
            border: 2px solid #34a853;
            box-shadow: 0 4px 12px rgba(52, 168, 83, 0.1);
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <div style='
                font-size: 16px;
                color: #5f6368;
                font-weight: 700;
                margin-bottom: 15px;
            '>
                📉 PRESUPUESTO RESTANTE
            </div>
            <div style='
                font-size: 28px;
                color: #34a853;
                font-weight: 900;
                line-height: 1.2;
                word-break: break-word;
            '>
                ${presupuesto_restante:,.0f}
            </div>
            <div style='
                font-size: 14px;
                color: #80868b;
                margin-top: 12px;
            '>
                Monto disponible
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # PORCENTAJE UTILIZADO
        porcentaje_utilizado = (presupuesto_consumido / presupuesto_total * 100) if presupuesto_total > 0 else 0
        
        # Determinar color según porcentaje
        if porcentaje_utilizado >= 90:
            color_porcentaje = '#ea4335'  # Rojo
            icono = '⚠️'
            texto_estado = 'Crítico'
        elif porcentaje_utilizado >= 70:
            color_porcentaje = '#fbbc04'  # Amarillo/Naranja
            icono = '📊'
            texto_estado = 'Moderado'
        elif porcentaje_utilizado >= 40:
            color_porcentaje = '#34a853'  # Verde
            icono = '✅'
            texto_estado = 'Disponible'
        else:
            color_porcentaje = '#0d652d'  # Verde oscuro
            icono = '🟢'
            texto_estado = 'Muy disponible'
        
        st.markdown(f"""
        <div style='
            background: white;
            border-radius: 15px;
            padding: 25px 15px;
            text-align: center;
            border: 2px solid {color_porcentaje};
            box-shadow: 0 4px 12px rgba(52, 168, 83, 0.1);
            height: 180px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        '>
            <div style='
                font-size: 16px;
                color: #5f6368;
                font-weight: 700;
                margin-bottom: 10px;
            '>
                {icono} % PRESUPUESTO UTILIZADO
            </div>
            <div style='
                font-size: 42px;
                color: {color_porcentaje};
                font-weight: 900;
                line-height: 1;
            '>
                {porcentaje_utilizado:.1f}%
            </div>
            <div style='
                font-size: 14px;
                color: #80868b;
                margin-top: 12px;
                padding: 4px 8px;
                background-color: {color_porcentaje}15;
                border-radius: 10px;
                font-weight: 600;
            '>
                Estado: {texto_estado}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Línea separadora
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ============================
    # FILTRO DE COMUNA Y TARJETAS
    # ============================
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

def _get_estado_utilizacion(porcentaje):
    """
    Determinar estado de utilización basado en porcentaje
    Esta función debería usar la misma lógica que ya tienes implementada
    en utils.py o cards.py
    """
    # Valores por defecto basados en tu imagen
    if porcentaje >= 90:
        return "POTENCIALMENTE AGOTADO"
    elif porcentaje >= 70:
        return "MODERADO"
    elif porcentaje >= 40:
        return "DISPONIBLE"
    else:
        return "MUY DISPONIBLE"

def _get_color_for_status(status):
    """
    Obtener color para el estado de utilización
    """
    status = str(status).upper()
    
    if "POTENCIALMENTE AGOTADO" in status:
        return '#ea4335'  # Rojo
    elif "MODERADO" in status:
        return '#fbbc04'  # Amarillo/Naranja
    elif "DISPONIBLE" in status:
        return '#34a853'  # Verde
    elif "MUY DISPONIBLE" in status:
        return '#0d652d'  # Verde oscuro
    else:
        return '#9aa0a6'  # Gris para otros casos

def _apply_color_to_status(status):
    """
    Aplicar color al texto del estado
    """
    color = _get_color_for_status(status)
    return f'background-color: {color}; color: white; font-weight: bold; border-radius: 10px; padding: 4px 8px; text-align: center;'