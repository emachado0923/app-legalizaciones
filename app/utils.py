# app/utils.py
import pandas as pd
import numpy as np
from app.config import COMUNA_MAPPING

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

def process_comuna_data(df):
    """Procesar y enriquecer datos de comunas"""
    if df.empty:
        return df
    
    # Asegurar columnas numéricas
    numeric_columns = ['presupuesto_comuna', 'restante_presupuesto_comuna', 
                      'acumulado_legali_comuna', 'numero_usuarios_comuna']
    
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
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
    """Calcular métricas resumidas del dataset"""
    if df.empty:
        return {
            'total_presupuesto': 0,
            'total_restante': 0,
            'total_usuarios': 0,
            'total_comunas': 0,
            'porcentaje_utilizacion': 0
        }
    
    total_presupuesto = df['presupuesto_comuna'].sum()
    total_restante = df['restante_presupuesto_comuna'].sum()
    total_usuarios = df['numero_usuarios_comuna'].sum()
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