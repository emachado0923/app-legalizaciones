# app/components/cards.py - CON VALORES COMPLETOS Y ENTEROS
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from app.utils import get_comuna_numero  # Importar función centralizada

# Mapeo de comunas con sus números (se mantiene por compatibilidad, pero se usará de utils)
COMUNA_NUMEROS = {
    "POPULAR": "01",
    "SANTA CRUZ": "02", 
    "MANRIQUE": "03",
    "ARANJUEZ": "04",
    "CASTILLA": "05",
    "DOCE DE OCTUBRE": "06",
    "ROBLEDO": "07",
    "VILLA HERMOSA": "08",
    "BUENOS AIRES": "09",
    "LA CANDELARIA": "10",
    "LAURELES/ESTADIO": "11",
    "LA AMERICA": "12",
    "SAN JAVIER": "13",
    "POBLADO": "14",
    "GUAYABAL": "15",
    "BELEN": "16",
    "SAN SEBASTIAN DE PALMITAS": "50",
    "SAN CRISTOBAL": "60",
    "ALTAVISTA": "70",
    "SAN ANTONIO DE PRADO": "80",
    "SANTA ELENA": "90"
}

def format_currency_complete(value):
    """Formatear valor como moneda COMPLETA sin abreviaturas - SOLO ENTEROS"""
    if pd.isna(value) or value is None:
        return "$ 0"
    try:
        # Convertir a entero
        value_int = int(float(value))
        # Mostrar con separadores de miles sin decimales
        return f"$ {value_int:,}"
    except (ValueError, TypeError):
        return "$ 0"

def format_number_integer(value):
    """Formatear número como entero sin decimales"""
    if pd.isna(value) or value is None:
        return "0"
    try:
        value_int = int(float(value))
        return f"{value_int:,}"
    except (ValueError, TypeError):
        return "0"

def get_status_color_tv(percentage):
    """Obtener color optimizado para TV según porcentaje"""
    if percentage >= 90:
        return "#ea4335"  # Rojo - ALTA URGENCIA
    elif percentage >= 70:
        return "#f9ab00"  # Amarillo - ATENCIÓN
    elif percentage >= 40:
        return "#34a853"  # Verde - DISPONIBLE
    else:
        return "#0b8043"  # Verde oscuro - MUY DISPONIBLE

def get_urgency_status(percentage):
    """Determinar estado de urgencia"""
    if percentage >= 90:
        return "urgent", "POTENCIALMENTE AGOTADO"
    elif percentage >= 70:
        return "warning", "MODERADO"
    elif percentage >= 40:
        return "ok", "DISPONIBLE"
    else:
        return "available", "MUY DISPONIBLE"

def create_estrato_resumen_card(estrato_text, estrato_class,
                               presupuesto, restante, usuarios, porcentaje, has_data=True):
    """Crear tarjeta de resumen para un estrato"""
    
    if not has_data:
        return f'''
        <div class="estrato-resumen-card no-data">
            <div class="estrato-resumen-header">
                <div class="estrato-resumen-title">{estrato_text}</div>
                <div class="estrato-resumen-badge {estrato_class}">RESUMEN</div>
            </div>
            
            <div class="no-data-state">
                <div class="no-data-icon">📭</div>
                <div class="no-data-title">NO APLICA</div>
                <div class="no-data-text">Esta comuna no tiene {estrato_text.replace("ESTRATOS ", "")}</div>
            </div>
        </div>
        '''
    
    consumido = presupuesto - restante
    bar_color = get_status_color_tv(porcentaje)
    urgency_class, urgency_text = get_urgency_status(porcentaje)
    
    return f'''
    <div class="estrato-resumen-card {urgency_class}">
        <!-- Encabezado del estrato -->
        <div class="estrato-resumen-header">
            <div class="estrato-resumen-title">{estrato_text}</div>
            <div class="estrato-resumen-badge {estrato_class}">RESUMEN</div>
        </div>
        
        <!-- Estado de urgencia -->
        <div class="estrato-resumen-status {urgency_class}">
            <span class="estrato-resumen-status-text">{urgency_text}</span>
        </div>
        
        <!-- Métricas principales -->
        <div class="estrato-resumen-metrics">
            <div class="estrato-metric-row">
                <span class="estrato-metric-label">Presupuesto Total</span>
                <span class="estrato-metric-value">{format_currency_complete(presupuesto)}</span>
            </div>
            
            <div class="estrato-metric-row">
                <span class="estrato-metric-label" style="color: #1a73e8;">Restante</span>
                <span class="estrato-metric-value" style="color: #1a73e8;">{format_currency_complete(restante)}</span>
            </div>
            
            <div class="estrato-metric-row">
                <span class="estrato-metric-label" style="color: #34a853;">Legalizados</span>
                <span class="estrato-metric-value" style="color: #34a853;">{format_number_integer(usuarios)}</span>
            </div>
        </div>
        
        <!-- Barra de progreso -->
        <div class="estrato-resumen-progress">
            <div class="estrato-resumen-progress-info">
                <span class="estrato-resumen-progress-label">Utilización</span>
                <span class="estrato-resumen-progress-value" style="color: {bar_color};">{porcentaje:.1f}%</span>
            </div>
            <div class="estrato-resumen-progress-bar">
                <div class="estrato-resumen-progress-fill" style="width: {porcentaje}%; background: {bar_color};"></div>
            </div>
        </div>
    </div>
    '''

def create_fiducias_card(fiducias_data, estrato_text, has_data=True):
    """Crear tarjeta con detalle de fiducias - VALORES ENTEROS"""
    
    if not has_data or fiducias_data.empty:
        return f'''
        <div class="fiducias-card no-data">
            <div class="fiducias-header no-data">
                <div class="fiducias-title">FIDUCIAS {estrato_text}</div>
            </div>
            <div class="no-data-state">
                <div class="no-data-icon">📭</div>
                <div class="no-data-title">NO APLICA</div>
                <div class="no-data-text">Esta comuna no tiene {estrato_text.replace("ESTRATOS ", "")}</div>
            </div>
        </div>
        '''
    
    # Ordenar fiducias por mayor a menor presupuesto
    fiducias_data = fiducias_data.sort_values('presupuesto_comuna', ascending=False)
    
    # Generar HTML para cada fiducia
    fiducias_html = ""
    for _, fiducia in fiducias_data.iterrows():
        fiducia_id = fiducia.get('idfiducia', 'N/A')
        
        # Asegurar que los valores sean enteros
        try:
            presupuesto = int(float(fiducia['presupuesto_comuna']))
            restante = int(float(fiducia['restante_presupuesto_comuna']))
        except (ValueError, TypeError):
            presupuesto = 0
            restante = 0
            
        consumido = presupuesto - restante
        porcentaje = (consumido / presupuesto * 100) if presupuesto > 0 else 0
        bar_color = get_status_color_tv(porcentaje)
        
        fiducias_html += f'''
        <div class="fiducia-item">
            <div class="fiducia-header">
                <div class="fiducia-id">Fiducia {fiducia_id}</div>
                <div class="fiducia-porcentaje" style="color: {bar_color};">{porcentaje:.1f}%</div>
            </div>
            
            <div class="fiducias-metrics">
                <div class="fiducia-metric">
                    <div class="fiducia-metric-label">Presupuesto</div>
                    <div class="fiducia-metric-value">{format_currency_complete(presupuesto)}</div>
                </div>
                <div class="fiducia-metric">
                    <div class="fiducia-metric-label">Restante</div>
                    <div class="fiducia-metric-value available">{format_currency_complete(restante)}</div>
                </div>
            </div>
            
            <div class="fiducias-progress">
                <div class="fiducia-progress-bar">
                    <div class="fiducia-progress-fill" style="width: {porcentaje}%; background: {bar_color};"></div>
                </div>
            </div>
        </div>
        '''
    
    return f'''
    <div class="fiducias-card">
        <div class="fiducias-header">
            <div class="fiducias-title">📦 FIDUCIAS {estrato_text}</div>
            <div class="fiducias-count">{len(fiducias_data)} fiducia(s)</div>
        </div>
        
        <div class="fiducias-list">
            {fiducias_html}
        </div>
    </div>
    '''

def create_comuna_estrato_row(comuna_nombre, estrato_text, estrato_class, 
                            resumen_data, fiducias_data):
    """Crear una fila con resumen y fiducias para un estrato"""
    
    has_data = resumen_data is not None and len(fiducias_data) > 0
    
    if has_data:
        # Asegurar que los valores sean enteros
        try:
            presupuesto = int(float(resumen_data['presupuesto_comuna']))
            restante = int(float(resumen_data['restante_presupuesto_comuna']))
            usuarios = int(float(resumen_data['numero_usuarios_comuna']))
        except (ValueError, TypeError):
            presupuesto = restante = usuarios = 0
            
        consumido = presupuesto - restante
        porcentaje = (consumido / presupuesto * 100) if presupuesto > 0 else 0
    else:
        presupuesto = restante = usuarios = porcentaje = 0
    
    return f'''
    <div class="estrato-row">
        <!-- Tarjeta de resumen (izquierda) -->
        {create_estrato_resumen_card(
            estrato_text=estrato_text,
            estrato_class=estrato_class,
            presupuesto=presupuesto,
            restante=restante,
            usuarios=usuarios,
            porcentaje=porcentaje,
            has_data=has_data
        )}
        
        <!-- Tarjeta de fiducias (derecha) -->
        {create_fiducias_card(fiducias_data, estrato_text, has_data)}
    </div>
    '''

def create_comuna_section(comuna_nombre, resumen_123, fiducias_123, resumen_456, fiducias_456):
    """Crear sección completa para una comuna"""
    
    # Usar la función importada desde utils.py
    comuna_numero = get_comuna_numero(comuna_nombre)
    
    return f'''
    <div class="comuna-section">
        <!-- Encabezado de la comuna -->
        <div class="comuna-section-header">
            <div class="comuna-section-numero">{comuna_numero}</div>
            <div class="comuna-section-nombre">{comuna_nombre}</div>
        </div>
        
        <!-- Línea 1: Estratos 1-3 -->
        {create_comuna_estrato_row(
            comuna_nombre=comuna_nombre,
            estrato_text="ESTRATOS 1-3",
            estrato_class="estrato-123",
            resumen_data=resumen_123,
            fiducias_data=fiducias_123
        )}
        
        <!-- Línea 2: Estratos 4-6 -->
        {create_comuna_estrato_row(
            comuna_nombre=comuna_nombre,
            estrato_text="ESTRATOS 4-6",
            estrato_class="estrato-456",
            resumen_data=resumen_456,
            fiducias_data=fiducias_456
        )}
    </div>
    '''

def create_fiducias_grid(df, grupo_estrato="Todos"):
    """Crear grid con nueva estructura de fiducias - VALORES ENTEROS"""
    
    if df.empty:
        st.warning("📭 No hay datos para mostrar")
        return
    
    # Preparar datos
    if 'Comuna Base' not in df.columns and 'Nombre Comuna' in df.columns:
        df['Comuna Base'] = df['Nombre Comuna'].apply(
            lambda x: str(x).split(' - ')[1] if ' - ' in str(x) else str(x)
        )
    
    # Separar datos por estrato
    df_123 = df[df['es_123'] == True].copy()
    df_456 = df[df['es_123'] == False].copy()
    
    # Filtrar según selección
    if grupo_estrato == "Estratos 1, 2 y 3":
        df_filtrado = df_123.copy()
        df_456 = pd.DataFrame()  # Vacío
    elif grupo_estrato == "Estratos 4, 5 y 6":
        df_filtrado = df_456.copy()
        df_123 = pd.DataFrame()  # Vacío
    else:
        df_filtrado = df.copy()
    
    # Obtener todas las comunas únicas del df filtrado
    all_comunas = sorted(df_filtrado['Comuna Base'].unique()) if not df_filtrado.empty else []
    
    # Obtener comunas de cada estrato para el agrupamiento
    comunas_123 = sorted(df_123['Comuna Base'].unique()) if not df_123.empty else []
    comunas_456 = sorted(df_456['Comuna Base'].unique()) if not df_456.empty else []
    
    # Para "Todos", necesitamos todas las comunas de ambos estratos
    if grupo_estrato == "Todos":
        all_comunas = sorted(set(list(comunas_123) + list(comunas_456)))
    
    if not all_comunas:
        st.info(f"📭 No hay datos para {grupo_estrato}")
        return
    
    # Ordenar comunas por número usando la función importada
    comunas_ordenadas = []
    for comuna in all_comunas:
        numero = get_comuna_numero(comuna)
        comunas_ordenadas.append((int(numero) if numero.isdigit() else 99, comuna))
    
    comunas_ordenadas.sort(key=lambda x: x[0])
    comunas_finales = [comuna for _, comuna in comunas_ordenadas]
    
    # Preparar datos agrupados por comuna - ASEGURAR VALORES ENTEROS
    comunas_data = {}
    
    for comuna in comunas_finales:
        # Datos para Estratos 1-3
        df_comuna_123 = df_123[df_123['Comuna Base'] == comuna]
        if not df_comuna_123.empty:
            # Sumar y convertir a enteros
            presupuesto_123 = int(df_comuna_123['presupuesto_comuna'].sum())
            restante_123 = int(df_comuna_123['restante_presupuesto_comuna'].sum())
            usuarios_123 = int(df_comuna_123['numero_usuarios_comuna'].sum())
            
            resumen_123 = {
                'presupuesto_comuna': presupuesto_123,
                'restante_presupuesto_comuna': restante_123,
                'numero_usuarios_comuna': usuarios_123
            }
            fiducias_123 = df_comuna_123[['idfiducia', 'presupuesto_comuna', 'restante_presupuesto_comuna']].copy()
        else:
            resumen_123 = None
            fiducias_123 = pd.DataFrame()
        
        # Datos para Estratos 4-6
        df_comuna_456 = df_456[df_456['Comuna Base'] == comuna]
        if not df_comuna_456.empty:
            # Sumar y convertir a enteros
            presupuesto_456 = int(df_comuna_456['presupuesto_comuna'].sum())
            restante_456 = int(df_comuna_456['restante_presupuesto_comuna'].sum())
            usuarios_456 = int(df_comuna_456['numero_usuarios_comuna'].sum())
            
            resumen_456 = {
                'presupuesto_comuna': presupuesto_456,
                'restante_presupuesto_comuna': restante_456,
                'numero_usuarios_comuna': usuarios_456
            }
            fiducias_456 = df_comuna_456[['idfiducia', 'presupuesto_comuna', 'restante_presupuesto_comuna']].copy()
        else:
            resumen_456 = None
            fiducias_456 = pd.DataFrame()
        
        comunas_data[comuna] = {
            'resumen_123': resumen_123,
            'fiducias_123': fiducias_123,
            'resumen_456': resumen_456,
            'fiducias_456': fiducias_456
        }
    
    # DEFINIR EL CSS DENTRO DE LA FUNCIÓN - CORREGIDO
    fiducias_css = '''
    <style>
    /* RESET */
    .fiducias-container * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    /* Contenedor principal */
    .comunas-sections {
        display: flex;
        flex-direction: column;
        gap: 40px;
        padding: 20px 10px;
    }
    
    /* Sección de comuna */
    .comuna-section {
        background: white;
        border-radius: 20px;
        padding: 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border: 3px solid #e0e0e0;
        overflow: hidden;
    }
    
    /* Encabezado de comuna */
    .comuna-section-header {
        background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%);
        padding: 15px 30px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .comuna-section-numero {
        font-size: 40px !important;
        font-weight: 900 !important;
        color: white !important;
        background: rgba(255, 255, 255, 0.2);
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        font-family: 'Inter', sans-serif !important;
    }
    
    .comuna-section-nombre {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: white !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
        flex-grow: 1;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Fila por estrato */
    .estrato-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0;
        border-top: 3px solid #f0f0f0;
    }
    
    /* Tarjeta de resumen */
    .estrato-resumen-card {
        padding: 25px;
        height: 100%;
        display: flex;
        flex-direction: column;
        min-height: 280px;
        border-right: 3px solid #f0f0f0;
        background: #f8f9fa;
    }
    
    /* Estados de urgencia para resumen */
    .estrato-resumen-card.urgent {
        border-left: 5px solid #d93025;
        background: linear-gradient(135deg, #ffffff 0%, #fce8e6 100%);
    }
    
    .estrato-resumen-card.warning {
        border-left: 5px solid #f9ab00;
        background: linear-gradient(135deg, #ffffff 0%, #fef7e0 100%);
    }
    
    .estrato-resumen-card.ok {
        border-left: 5px solid #34a853;
        background: linear-gradient(135deg, #ffffff 0%, #e6f4ea 100%);
    }
    
    .estrato-resumen-card.available {
        border-left: 5px solid #0b8043;
        background: linear-gradient(135deg, #ffffff 0%, #d5e8d9 100%);
    }
    
    /* Estado "NO APLICA" */
    .estrato-resumen-card.no-data {
        background: #f8f9fa;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-left: 5px solid #80868b;
    }
    
    .no-data-state {
        text-align: center;
        padding: 20px;
    }
    
    .no-data-icon {
        font-size: 48px;
        margin-bottom: 15px;
        opacity: 0.5;
        color: #80868b;
    }
    
    .no-data-title {
        font-size: 22px !important;
        font-weight: 800 !important;
        color: #80868b !important;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    
    .no-data-text {
        font-size: 16px;
        color: #9aa0a6;
        max-width: 250px;
        margin: 0 auto;
    }
    
    .estrato-resumen-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    
    .estrato-resumen-title {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #202124 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .estrato-resumen-badge {
        padding: 6px 12px;
        border-radius: 15px;
        font-size: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: 'Inter', sans-serif !important;
    }
    
    .estrato-resumen-badge.estrato-123 {
        background-color: #e8f0fe;
        color: #1a73e8 !important;
        border: 2px solid #1a73e8;
    }
    
    .estrato-resumen-badge.estrato-456 {
        background-color: #e6f4ea;
        color: #0d652d !important;
        border: 2px solid #0d652d;
    }
    
    .estrato-resumen-status {
        padding: 10px;
        border-radius: 10px;
        font-size: 18px !important;
        font-weight: 800 !important;
        text-align: center;
        margin: 15px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Inter', sans-serif !important;
    }
    
    .estrato-resumen-status.urgent {
        background-color: #d93025;
        color: white !important;
    }
    
    .estrato-resumen-status.warning {
        background-color: #f9ab00;
        color: #202124 !important;
    }
    
    .estrato-resumen-status.ok {
        background-color: #34a853;
        color: white !important;
    }
    
    .estrato-resumen-status.available {
        background-color: #0b8043;
        color: white !important;
    }
    
    .estrato-resumen-metrics {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .estrato-metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .estrato-metric-label {
        font-size: 16px !important;
        color: #5f6368;
        font-weight: 600;
        font-family: 'Roboto', sans-serif !important;
    }
    
    .estrato-metric-value {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: #202124;
        font-family: 'Inter', sans-serif !important;
        text-align: right;
        min-width: 150px;
    }
    
    .estrato-resumen-progress {
        margin-top: 20px;
    }
    
    .estrato-resumen-progress-info {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    
    .estrato-resumen-progress-label {
        font-size: 14px !important;
        color: #5f6368;
        font-weight: 600;
        font-family: 'Roboto', sans-serif !important;
    }
    
    .estrato-resumen-progress-value {
        font-size: 20px !important;
        font-weight: 900 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .estrato-resumen-progress-bar {
        height: 10px;
        background-color: #eaedf2;
        border-radius: 5px;
        overflow: hidden;
        border: 1px solid #dadce0;
    }
    
    .estrato-resumen-progress-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 1s ease;
    }
    
    /* Tarjeta de fiducias */
    .fiducias-card {
        padding: 25px;
        height: 100%;
        display: flex;
        flex-direction: column;
        min-height: 280px;
        background: white;
        overflow-y: auto;
    }
    
    .fiducias-card.no-data {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background: #f8f9fa;
        border-left: 5px solid #80868b;
    }
    
    .fiducias-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .fiducias-header.no-data {
        justify-content: center;
        border-bottom: none;
    }
    
    .fiducias-title {
        font-size: 20px !important;
        font-weight: 800 !important;
        color: #1a73e8 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .fiducias-title.no-data {
        color: #80868b !important;
    }
    
    .fiducias-count {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #5f6368;
        background: #f0f2f6;
        padding: 4px 10px;
        border-radius: 12px;
        font-family: 'Roboto', sans-serif !important;
    }
    
    .fiducias-list {
        flex-grow: 1;
        overflow-y: auto;
        padding-right: 5px;
    }
    
    .fiducia-item {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .fiducia-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        border-color: #1a73e8;
    }
    
    .fiducia-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .fiducia-id {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #202124;
        font-family: 'Inter', sans-serif !important;
    }
    
    .fiducia-porcentaje {
        font-size: 14px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .fiducias-metrics {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-bottom: 10px;
    }
    
    .fiducia-metric {
        text-align: center;
    }
    
    .fiducia-metric-label {
        font-size: 12px;
        color: #5f6368;
        font-weight: 500;
        margin-bottom: 4px;
        font-family: 'Roboto', sans-serif !important;
    }
    
    .fiducia-metric-value {
        font-size: 14px;
        font-weight: 700;
        color: #202124;
        font-family: 'Inter', sans-serif !important;
        word-break: break-word;
    }
    
    .fiducia-metric-value.available {
        color: #34a853;
    }
    
    .fiducias-progress {
        margin-top: 10px;
    }
    
    .fiducia-progress-bar {
        height: 6px;
        background-color: #eaedf2;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .fiducia-progress-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 1s ease;
    }
    
    /* Responsive */
    @media (max-width: 1200px) {
        .comuna-section-nombre {
            font-size: 28px !important;
        }
        
        .comuna-section-numero {
            font-size: 36px !important;
            width: 55px;
            height: 55px;
        }
        
        .estrato-resumen-title {
            font-size: 20px !important;
        }
        
        .fiducias-title {
            font-size: 18px !important;
        }
        
        .estrato-metric-value {
            font-size: 16px !important;
            min-width: 120px;
        }
    }
    
    @media (max-width: 768px) {
        .estrato-row {
            grid-template-columns: 1fr;
        }
        
        .estrato-resumen-card {
            border-right: none;
            border-bottom: 3px solid #f0f0f0;
        }
        
        .estrato-metric-value {
            min-width: 100px;
        }
    }
    </style>
    '''
    
    # Generar HTML
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
        {fiducias_css}
    </head>
    <body>
        <div class="fiducias-container">
            <div class="comunas-sections">
    '''
    
    # Generar secciones para cada comuna
    for comuna in comunas_finales:
        data = comunas_data[comuna]
        html_content += create_comuna_section(
            comuna_nombre=comuna,
            resumen_123=data['resumen_123'],
            fiducias_123=data['fiducias_123'],
            resumen_456=data['resumen_456'],
            fiducias_456=data['fiducias_456']
        )
    
    html_content += '''
            </div>
        </div>
    </body>
    </html>
    '''
    
    # Mostrar estadísticas - VALORES ENTEROS
    col1, col2, col3 = st.columns(3)
    with col1:
        total_fiducias = len(df_filtrado['idfiducia'].unique()) if 'idfiducia' in df_filtrado.columns else 0
        fiducias_123_count = len(df_123['idfiducia'].unique()) if 'idfiducia' in df_123.columns else 0
        fiducias_456_count = len(df_456['idfiducia'].unique()) if 'idfiducia' in df_456.columns else 0
        st.metric(
            label="FIDUCIAS TOTALES",
            value=total_fiducias,
            delta=f"1-3: {fiducias_123_count} | 4-6: {fiducias_456_count}"
        )
    
    with col2:
        total_presupuesto = int(df_filtrado['presupuesto_comuna'].sum()) if not df_filtrado.empty else 0
        st.metric("PRESUPUESTO TOTAL", format_currency_complete(total_presupuesto))
    
    with col3:
        total_usuarios = int(df_filtrado['numero_usuarios_comuna'].sum()) if not df_filtrado.empty else 0
        st.metric("LEGALIZADOS", f"{total_usuarios:,}")
    
    # Mostrar el grid
    st.markdown("---")
    components.html(html_content, height=1200, scrolling=True)
    
    # Leyenda
    with st.expander("📋 LEYENDA - ESTADOS DE UTILIZACIÓN", expanded=True):
        cols = st.columns(4)
        estados = [
            ("POTENCIALMENTE AGOTADO", ">= 90% usado", "#d93025", "#fce8e6"),
            ("MODERADO", "70-89% usado", "#f9ab00", "#fef7e0"),
            ("DISPONIBLE", "40-70% usado", "#34a853", "#e6f4ea"),
            ("MUY DISPONIBLE", "< 40% usado", "#0b8043", "#d5e8d9")
        ]
        
        for idx, (nombre, desc, color, bg_color) in enumerate(estados):
            with cols[idx]:
                st.markdown(f"""
                <div style="text-align: center; padding: 12px; background: {bg_color}; 
                         border-radius: 10px; border: 3px solid {color}; margin-bottom: 10px;
                         font-family: 'Roboto', sans-serif;">
                    <div style="font-weight: 900; color: {color}; font-size: 16px;">{nombre}</div>
                    <div style="color: #666; font-size: 14px;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)

def create_tv_cards_grid(df, grupo_estrato="Todos"):
    """Función principal que llama a la nueva estructura"""
    return create_fiducias_grid(df, grupo_estrato)