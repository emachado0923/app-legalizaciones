# app/pages/detail.py
import streamlit as st
import pandas as pd
from app.utils import format_currency
from app.components import render_comuna_metrics

def render_detail_page(df):
    """Renderizar página de detalle por comuna"""
    st.markdown("## 📋 Detalle por Comuna - Tabla de Fiducias")
    
    if df.empty:
        st.warning("No hay datos disponibles para mostrar.")
        return
    
    # Selector de comuna
    if 'Nombre Comuna' in df.columns:
        comunas_disponibles = sorted(df['Nombre Comuna'].unique())
        comuna_seleccionada = st.selectbox(
            "Seleccione una comuna",
            options=comunas_disponibles,
            index=0
        )
        
        # Filtrar datos de la comuna seleccionada
        df_comuna = df[df['Nombre Comuna'] == comuna_seleccionada]
        
        if not df_comuna.empty:
            st.markdown(f"### 📍 {comuna_seleccionada}")
            
            # Mostrar métricas de la comuna
            render_comuna_metrics(df_comuna)
            
            st.markdown("---")
            
            # Tabla detallada de fiducias
            st.markdown("#### 📊 Resumen por Fiducia")
            
            # Preparar datos para la tabla
            table_data = []
            for _, row in df_comuna.iterrows():
                table_data.append({
                    'Fiducia': row.get('idfiducia', 'N/A'),
                    'Presupuesto Inicial': format_currency(row.get('presupuesto_comuna', 0)),
                    'Restante': format_currency(row.get('restante_presupuesto_comuna', 0)),
                    'Consumido': format_currency(
                        row.get('presupuesto_comuna', 0) - row.get('restante_presupuesto_comuna', 0)
                    ),
                    'Usuarios': int(row.get('numero_usuarios_comuna', 0))
                })
            
            # Crear DataFrame
            summary_df = pd.DataFrame(table_data)
            
            # Agregar fila de totales
            if not summary_df.empty:
                total_row = {
                    'Fiducia': '**TOTAL**',
                    'Presupuesto Inicial': format_currency(df_comuna['presupuesto_comuna'].sum()),
                    'Restante': format_currency(df_comuna['restante_presupuesto_comuna'].sum()),
                    'Consumido': format_currency(
                        df_comuna['presupuesto_comuna'].sum() - df_comuna['restante_presupuesto_comuna'].sum()
                    ),
                    'Usuarios': int(df_comuna['numero_usuarios_comuna'].sum())
                }
                
                summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)
                
                # Mostrar tabla
                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    height=400
                )
                
                # Botón para exportar
                csv = summary_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar datos de la comuna",
                    data=csv,
                    file_name=f"detalle_{comuna_seleccionada.replace(' ', '_').replace('-', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No hay datos de fiducias para esta comuna.")
        else:
            st.warning(f"No se encontraron datos para la comuna {comuna_seleccionada}")
    else:
        st.warning("No se encontró la columna 'Nombre Comuna' en los datos")