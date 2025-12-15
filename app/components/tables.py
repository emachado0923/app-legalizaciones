# app/components/tables.py
import pandas as pd
from app.utils import format_currency

def create_summary_table(df, grupo_estrato="Todos"):
    """Crear tabla de resumen similar a Power BI"""
    if df.empty:
        return pd.DataFrame()
    
    # Filtrar por grupo de estrato si no es "Todos"
    if grupo_estrato != "Todos":
        if grupo_estrato == "Estratos 1, 2 y 3":
            df_filtered = df[df['es_123'] == True]
        else:
            df_filtered = df[df['es_123'] == False]
    else:
        df_filtered = df.copy()
    
    if df_filtered.empty:
        return pd.DataFrame()
    
    try:
        # Crear resumen por comuna
        agg_dict = {}
        
        if 'presupuesto_comuna' in df_filtered.columns:
            agg_dict['presupuesto_comuna'] = 'sum'
        
        if 'restante_presupuesto_comuna' in df_filtered.columns:
            agg_dict['restante_presupuesto_comuna'] = 'sum'
        
        if 'numero_usuarios_comuna' in df_filtered.columns:
            agg_dict['numero_usuarios_comuna'] = 'sum'
        
        if 'acumulado_legali_comuna' in df_filtered.columns:
            agg_dict['acumulado_legali_comuna'] = 'sum'
        
        summary = df_filtered.groupby('Comuna Base').agg(agg_dict).reset_index()
        
        # Calcular campos adicionales
        if 'presupuesto_comuna' in summary.columns and 'restante_presupuesto_comuna' in summary.columns:
            summary['Consumido'] = summary['presupuesto_comuna'] - summary['restante_presupuesto_comuna']
            summary['% Participación'] = (summary['Consumido'] / summary['presupuesto_comuna'] * 100).round(1)
        else:
            summary['Consumido'] = 0
            summary['% Participación'] = 0
        
        # Calcular cupos aproximados
        if 'numero_usuarios_comuna' in summary.columns:
            summary['Cupos aprox.'] = (summary['numero_usuarios_comuna'] * 1.5).round(0).astype(int)
        else:
            summary['Cupos aprox.'] = 0
        
        summary['Otorgado proyec'] = summary['Consumido']
        summary['Val proyec fidu'] = summary.apply(
            lambda row: 'S' if row['Consumido'] > 0 else 'NO', axis=1
        )
        
        # Construir la tabla final
        column_mapping = {
            'Comuna Base': 'Comuna',
            'Cupos aprox.': 'Cupos aprox.',
            'presupuesto_comuna': 'Disponible fidu',
            'numero_usuarios_comuna': 'Legalizados',
            'acumulado_legali_comuna': 'Acumulado legal',
            'Otorgado proyec': 'Otorgado proyec',
            'Val proyec fidu': 'Val proyec fidu',
            'restante_presupuesto_comuna': 'Presupuesto restante',
            '% Participación': '% participacion'
        }
        
        # Seleccionar y renombrar columnas
        available_columns = [col for col in column_mapping.keys() if col in summary.columns]
        summary = summary[available_columns].rename(columns=column_mapping)
        
        # Aplicar formato
        if 'Disponible fidu' in summary.columns:
            summary['Disponible fidu'] = summary['Disponible fidu'].apply(format_currency)
        
        if 'Otorgado proyec' in summary.columns:
            summary['Otorgado proyec'] = summary['Otorgado proyec'].apply(format_currency)
        
        if 'Presupuesto restante' in summary.columns:
            summary['Presupuesto restante'] = summary['Presupuesto restante'].apply(format_currency)
        
        if '% participacion' in summary.columns:
            summary['% participacion'] = summary['% participacion'].apply(lambda x: f"{x} %")
        
        return summary
    
    except Exception as e:
        import streamlit as st
        st.error(f"Error creando tabla de resumen: {e}")
        return pd.DataFrame()