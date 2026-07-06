# app/pages/citas.py - VERSIÓN CORREGIDA CON width='stretch'
import streamlit as st
import pandas as pd
import re
from datetime import datetime
from app.utils import get_colombia_time, format_colombia_time
from app.database import db

def extraer_nombre_y_documento(texto):
    """
    Extrae nombre y documento de un string con formato "Nombre - Documento"
    """
    if not isinstance(texto, str):
        return ("No disponible", "")
    
    patron = r'(.+?)\s*-\s*(\d+)'
    match = re.search(patron, texto)
    
    if match:
        nombre = match.group(1).strip()
        documento = match.group(2).strip()
        return (nombre, documento)
    else:
        return (texto.strip(), "")

def procesar_citas(df):
    """
    Procesa el DataFrame de citas para extraer nombre y documento
    """
    if df.empty:
        return df
    
    df_procesado = df.copy()
    
    if 'nombre' in df_procesado.columns:
        extracciones = df_procesado['nombre'].apply(extraer_nombre_y_documento)
        df_procesado[['nombre_persona', 'documento']] = pd.DataFrame(
            extracciones.tolist(), 
            index=df_procesado.index
        )
    
    return df_procesado

def get_citas_by_documento(documento):
    """
    Obtiene las citas SOLO por documento
    """
    results = db.get_citas_by_documento(documento)
    
    if results:
        df = pd.DataFrame(results)
        df = procesar_citas(df)
        return df
    else:
        return pd.DataFrame()

def es_documento_valido(documento):
    """
    Valida que el input sea un documento válido (solo números)
    """
    if not documento:
        return False
    
    documento_limpio = str(documento).strip()
    return documento_limpio.isdigit()

def render_citas_page():
    """Renderiza la página de consulta de citas SOLO por documento"""
    
    # Inicializar variables de session_state
    if 'citas_data' not in st.session_state:
        st.session_state.citas_data = None
    
    if 'last_documento' not in st.session_state:
        st.session_state.last_documento = ""
    
    if 'ultima_actualizacion' not in st.session_state:
        st.session_state.ultima_actualizacion = get_colombia_time()
    
    # Títulos
    st.markdown("<h1 style='text-align: center; color: #1a73e8; margin-bottom: 10px;'>📋 CONSULTA DE CITAS POR DOCUMENTO</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #5f6368; margin-bottom: 30px;'>Sapiencia - Seguimiento de Legalización</h3>", 
                unsafe_allow_html=True)
    
    # Contenedor principal
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Panel de búsqueda SOLO DOCUMENTO
        st.markdown("### 🔍 Búsqueda por Documento")
        
        # Input SOLO para documento
        documento = st.text_input(
            "**Número de Documento**",
            placeholder="Ej: 123456789",
            help="Ingrese SOLO el número de documento (sin puntos, comas o espacios)",
            key="input_documento_citas"
        )
        
        # Botón de búsqueda - ACTUALIZA LOS DATOS AL PRESIONAR
        buscar = st.button("🔍 Buscar Citas", type="primary", width='stretch')
        
        # Botón Limpiar Búsqueda
        if st.button("🧹 Limpiar Búsqueda", width='stretch'):
            st.session_state.citas_data = None
            st.session_state.last_documento = ""
            st.session_state.ultima_actualizacion = get_colombia_time()
            st.rerun()
        
        # Línea separadora
        st.markdown("---")
        
        # Mostrar última actualización
        last_update = format_colombia_time(st.session_state.ultima_actualizacion)
        
        # Tarjeta de última actualización
        st.markdown(f"""
        <div style='
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #1a73e8;
            margin: 15px 0 5px 0;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        '>
            <div style='font-size: 12px; color: #5f6368; font-weight: 600; margin-bottom: 3px;'>
                📅 ÚLTIMA ACTUALIZACIÓN
            </div>
            <div style='font-size: 14px; color: #202124; font-weight: 700;'>
                {last_update}
            </div>
            <div style='font-size: 11px; color: #80868b; margin-top: 8px;'>
                Datos actualizados al presionar "Buscar Citas"
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mostrar estadísticas si hay datos
        if st.session_state.citas_data is not None and not st.session_state.citas_data.empty:
            df_citas = st.session_state.citas_data
            
            total = len(df_citas)
            
            if 'estado' in df_citas.columns:
                asistidas = df_citas['estado'].str.contains('Asistida', case=False, na=False).sum()
            else:
                asistidas = 0
            
            st.markdown("---")
            st.markdown("#### 📊 Estadísticas")
            
            col1_stat, col2_stat = st.columns(2)
            with col1_stat:
                st.metric("Total Citas", total)
            with col2_stat:
                st.metric("Asistidas", asistidas)
    
    with col2:
        # Panel de resultados
        if st.session_state.citas_data is not None:
            df_citas = st.session_state.citas_data
            
            if not df_citas.empty:
                # MOSTRAR INFORMACIÓN DE LA PERSONA
                if 'documento' in df_citas.columns and 'nombre_persona' in df_citas.columns:
                    documentos = df_citas['documento'].dropna().unique()
                    nombres = df_citas['nombre_persona'].dropna().unique()
                    
                    if len(documentos) > 0 and len(nombres) > 0:
                        documento_principal = documentos[0]
                        nombre_principal = nombres[0]
                        
                        # Mostrar en grande
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); 
                                 padding: 30px; border-radius: 15px; 
                                 margin-bottom: 25px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
                            <h1 style='color: white; margin: 0 0 10px 0; font-size: 32px; font-weight: 700;'>👤 {nombre_principal}</h1>
                            <p style='color: rgba(255,255,255,0.95); margin: 0; font-size: 22px; font-weight: 500;'>
                                <strong>Documento:</strong> {documento_principal}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Mostrar información de búsqueda
                documento_actual = st.session_state.last_documento
                if documento_actual:
                    st.info(f"🔍 Mostrando {len(df_citas)} citas para el documento: **{documento_actual}**")
                
                # PREPARAR Y MOSTRAR LA TABLA
                df_display = df_citas.copy()
                
                # Definir columnas para mostrar
                columnas_a_mostrar = []
                
                if 'fecha' in df_display.columns:
                    columnas_a_mostrar.append('fecha')
                    try:
                        df_display['fecha'] = pd.to_datetime(df_display['fecha']).dt.strftime('%d/%m/%Y')
                    except:
                        pass
                
                if 'hora_inicio' in df_display.columns:
                    columnas_a_mostrar.append('hora_inicio')
                    try:
                        df_display['hora_inicio'] = pd.to_datetime(
                            df_display['hora_inicio'], 
                            format='%H:%M:%S',
                            errors='coerce'
                        ).dt.strftime('%I:%M %p')
                    except:
                        pass
                
                if 'taquilla' in df_display.columns:
                    columnas_a_mostrar.append('taquilla')
                
                if 'estado' in df_display.columns:
                    columnas_a_mostrar.append('estado')
                
                # Renombrar columnas
                rename_map = {
                    'fecha': 'Fecha',
                    'hora_inicio': 'Hora',
                    'taquilla': 'Taquilla',
                    'estado': 'Estado'
                }
                
                columnas_a_mostrar = [col for col in columnas_a_mostrar if col in df_display.columns]
                
                if columnas_a_mostrar:
                    df_display = df_display[columnas_a_mostrar]
                    df_display = df_display.rename(columns=rename_map)
                    
                    # Aplicar estilos
                    def color_estado(val):
                        if str(val).strip().lower() == 'asistida':
                            return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                        elif 'no' in str(val).lower():
                            return 'background-color: #f8d7da; color: #721c24;'
                        else:
                            return ''
                    
                    styled_df = df_display.style.map(
                        color_estado, 
                        subset=['Estado'] if 'Estado' in df_display.columns else []
                    ).set_properties(**{
                        'text-align': 'center',
                        'font-size': '14px'
                    })
                    
                    # Mostrar tabla con width='stretch' en lugar de use_container_width=True
                    st.dataframe(
                        styled_df,
                        width='stretch',
                        height=min(500, len(df_display) * 40 + 50)
                    )
                    
                    # Botón para descargar
                    csv = df_display.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"citas_{st.session_state.last_documento}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        width='stretch'
                    )
                else:
                    st.warning("No hay datos para mostrar")
            else:
                # DataFrame vacío
                if st.session_state.last_documento:
                    st.warning(f"⚠️ No se encontraron citas para el documento: **{st.session_state.last_documento}**")
                    st.info("Verifique que el número de documento sea correcto.")
        else:
            # Estado inicial - mostrar instrucciones
            st.markdown("""
            <div style='background: #f8f9fa; padding: 80px 20px; border-radius: 15px; 
                     text-align: center; margin-top: 60px; border: 2px dashed #ddd;'>
                <div style='font-size: 64px; color: #ddd; margin-bottom: 20px;'>🔍</div>
                <h2 style='color: #5f6368; margin-bottom: 15px;'>Consulta de Citas</h2>
                <p style='color: #80868b; font-size: 16px; max-width: 400px; margin: 0 auto; line-height: 1.6;'>
                    Ingrese el <strong>número de documento</strong> en el panel izquierdo y<br>
                    presione <strong>"Buscar Citas"</strong> para consultar el historial.
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # LÓGICA PRINCIPAL DE BÚSQUEDA - SE EJECUTA AL PRESIONAR EL BOTÓN
    if buscar:
        if not documento:
            st.warning("⚠️ Por favor ingrese un número de documento")
            st.stop()  # Detener ejecución aquí
        
        elif not es_documento_valido(documento):
            st.error("❌ El documento debe contener solo números")
            st.stop()  # Detener ejecución aquí
        
        else:
            # Mostrar spinner mientras se buscan los datos
            with st.spinner("🔍 Buscando citaciones..."):
                # OBTENER DATOS ACTUALIZADOS DE LA BASE DE DATOS
                df_citas = get_citas_by_documento(documento)
                
                # ACTUALIZAR session_state con los nuevos datos
                st.session_state.citas_data = df_citas
                st.session_state.last_documento = documento
                st.session_state.ultima_actualizacion = get_colombia_time()
                
                # Forzar rerun para mostrar los datos actualizados
                st.rerun()

if __name__ == "__main__":
    render_citas_page()