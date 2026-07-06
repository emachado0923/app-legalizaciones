# app/utils.py
import pandas as pd
import numpy as np
import re
from app.config import COMUNA_MAPPING
from datetime import datetime, timedelta

# Mapeo de números de comuna (debería estar en config o importarse de cards.py)
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

def format_currency(value):
    """Formatear valor como moneda SIN REDONDEAR - mostrar completo"""
    if pd.isna(value) or value is None:
        return "$ 0"
    try:
        value = float(value)
        # SIEMPRE mostrar con 3 decimales para precisión
        if value >= 1e9:  # Billones
            return f"$ {value/1e9:,.3f}B"  # 3 decimales: $ 2.600B
        elif value >= 1e6:  # Millones
            return f"$ {value/1e6:,.3f}M"  # 3 decimales: $ 28.600M
        elif value >= 1e3:  # Miles
            return f"$ {value/1e3:,.1f}K"  # 1 decimal: $ 1.5K
        else:
            return f"$ {value:,.0f}"  # Sin decimales: $ 500
    except (ValueError, TypeError):
        return "$ 0"

def get_status_color(percentage):
    """Obtener color según porcentaje de utilización"""
    if percentage >= 80:
        return "#ea4335"  # Rojo
    elif percentage >= 60:
        return "#f9ab00"  # Amarillo
    else:
        return "#34a853"  # Verde

def get_comuna_numero(comuna_nombre):
    """Obtener número de comuna a partir del nombre"""
    if not comuna_nombre or pd.isna(comuna_nombre):
        return "00"
    
    comuna_upper = str(comuna_nombre).upper().strip()
    for comuna, numero in COMUNA_NUMEROS.items():
        if comuna in comuna_upper or comuna_upper in comuna:
            return numero
    # Intentar extraer número del texto
    match = re.search(r'(\d{2})', comuna_upper)
    if match:
        return match.group(1)
    return "00"

def format_comuna_con_numero(comuna_nombre):
    """Formatear comuna con número: '01 - Popular'"""
    if not comuna_nombre or comuna_nombre == "TODAS LAS COMUNAS":
        return comuna_nombre
    
    numero = get_comuna_numero(comuna_nombre)
    return f"{numero} - {comuna_nombre}"

def get_comunas_formateadas(df):
    """Obtener lista de comunas formateadas con números"""
    if 'Comuna Base' not in df.columns and 'Nombre Comuna' in df.columns:
        df['Comuna Base'] = df['Nombre Comuna'].apply(
            lambda x: str(x).split(' - ')[1] if ' - ' in str(x) else str(x)
        )
    
    if 'Comuna Base' not in df.columns:
        return [], {}
    
    comunas_disponibles = sorted(df['Comuna Base'].unique())
    
    # Crear opciones formateadas
    opciones_comuna = ["TODAS LAS COMUNAS"]
    opciones_comuna += [format_comuna_con_numero(comuna) for comuna in comunas_disponibles]
    
    # Crear mapeo de opción formateada a nombre real
    opcion_a_nombre = {"TODAS LAS COMUNAS": "TODAS LAS COMUNAS"}
    for comuna in comunas_disponibles:
        opcion_formateada = format_comuna_con_numero(comuna)
        opcion_a_nombre[opcion_formateada] = comuna
    
    return opciones_comuna, opcion_a_nombre

def process_comuna_data(df):
    """Procesar y enriquecer datos de comunas - CONVERSIÓN A ENTEROS"""
    if df.empty:
        return df
    
    # Asegurar columnas numéricas - CONVERTIR A ENTEROS
    numeric_columns = ['presupuesto_comuna', 'restante_presupuesto_comuna', 
                      'acumulado_legali_comuna', 'numero_usuarios_comuna']
    
    for col in numeric_columns:
        if col in df.columns:
            # Convertir a float primero para manejar NaN, luego a int
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            # Convertir a enteros (redondear hacia abajo)
            df[col] = df[col].astype(int)
        else:
            df[col] = 0
    
    # Identificar tipo de estrato
    if 'comuna' in df.columns:
        df['comuna_str'] = df['comuna'].astype(str)
        df['es_123'] = df['comuna_str'].str.contains('123')
        df['grupo_estrato'] = df['es_123'].apply(
            lambda x: 'Estratos 1, 2 y 3' if x else 'Estratos 4, 5 y 6'
        )
        
        # Agregar nombre de comuna
        df['Nombre Comuna'] = df['comuna_str'].map(COMUNA_MAPPING)
        df['Nombre Comuna'] = df['Nombre Comuna'].fillna('Comuna ' + df['comuna_str'])
        
        # Extraer nombre base de comuna
        df['Comuna Base'] = df['Nombre Comuna'].apply(
            lambda x: x.split(' - ')[1] if ' - ' in str(x) else str(x)
        )
    
    return df

def calculate_summary_metrics(df):
    """Calcular métricas resumidas del dataset - VALORES ENTEROS"""
    if df.empty:
        return {
            'total_presupuesto': 0,
            'total_restante': 0,
            'total_usuarios': 0,
            'total_comunas': 0,
            'porcentaje_utilizacion': 0
        }
    
    total_presupuesto = int(df['presupuesto_comuna'].sum())
    total_restante = int(df['restante_presupuesto_comuna'].sum())
    total_usuarios = int(df['numero_usuarios_comuna'].sum())
    total_comunas = df['Nombre Comuna'].nunique() if 'Nombre Comuna' in df.columns else 0
    
    if total_presupuesto > 0:
        porcentaje_utilizacion = ((total_presupuesto - total_restante) / total_presupuesto * 100)
    else:
        porcentaje_utilizacion = 0
    
    return {
        'total_presupuesto': total_presupuesto,
        'total_restante': total_restante,
        'total_usuarios': total_usuarios,
        'total_comunas': total_comunas,
        'porcentaje_utilizacion': porcentaje_utilizacion
    }


def get_colombia_time():
    """
    Obtiene la hora actual en zona horaria de Colombia (UTC-5)
    No requiere pytz, usa cálculo manual
    """
    # Obtener hora UTC
    utc_now = datetime.utcnow()
    
    # Colombia está en UTC-5 (no tiene horario de verano)
    # Ajustar por 5 horas atrás
    colombia_time = utc_now - timedelta(hours=5)
    
    return colombia_time

def format_colombia_time(datetime_obj=None, formato='%d/%m/%Y %I:%M %p'):
    """
    Formatea una hora para mostrar en formato Colombia
    Si no se pasa datetime_obj, usa la hora actual Colombia
    
    Args:
        datetime_obj: datetime object (opcional)
        formato: string con formato deseado
        
    Returns:
        string con hora formateada
    """
    if datetime_obj is None:
        datetime_obj = get_colombia_time()
    
    return datetime_obj.strftime(formato)

def get_time_with_timezone():
    """
    Obtiene la hora actual con información de zona horaria
    Útil para mostrar en la interfaz
    """
    col_time = get_colombia_time()
    formatted = format_colombia_time(col_time)
    return f"{formatted} (Hora Colombia)"