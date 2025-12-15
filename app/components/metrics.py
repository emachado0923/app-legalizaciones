# app/components/metrics.py - SOLO USUARIOS LEGALIZADOS
import streamlit as st
from app.utils import format_currency

# app/components/metrics.py - CORREGIDO
import streamlit as st
from app.utils import format_currency

def render_global_metrics(metrics):
    """Renderizar SOLO la métrica de usuarios legalizados"""
    
    # Obtener usuarios por estrato
    usuarios_123 = 0
    usuarios_456 = 0
    if 'df' in metrics:
        df = metrics['df']
        usuarios_123 = df[df['es_123'] == True]['numero_usuarios_comuna'].sum() if 'es_123' in df.columns else 0
        usuarios_456 = df[df['es_123'] == False]['numero_usuarios_comuna'].sum() if 'es_123' in df.columns else 0
    
    porcentaje_123 = (usuarios_123 / metrics['total_usuarios'] * 100) if metrics['total_usuarios'] > 0 else 0
    porcentaje_456 = (usuarios_456 / metrics['total_usuarios'] * 100) if metrics['total_usuarios'] > 0 else 0
    
    # Crear el HTML como string
    html_content = f"""
    <div class="single-metric-container">
        <div class="single-metric-card">
            <!-- Encabezado -->
            <div class="single-metric-header">
                <div class="single-metric-title">👥 USUARIOS LEGALIZADOS</div>
                <div class="single-metric-total">{metrics['total_usuarios']:,.0f}</div>
            </div>
            
            <!-- Distribución detallada -->
            <div class="single-metric-details">
                <div class="detail-column">
                    <div class="detail-label">Estratos 1-3</div>
                    <div class="detail-value estrato-123">{usuarios_123:,.0f}</div>
                    <div class="detail-percent">{porcentaje_123:.1f}%</div>
                </div>
                
                <div class="detail-separator"></div>
                
                <div class="detail-column">
                    <div class="detail-label">Estratos 4-6</div>
                    <div class="detail-value estrato-456">{usuarios_456:,.0f}</div>
                    <div class="detail-percent">{porcentaje_456:.1f}%</div>
                </div>
            </div>
            
            <!-- Barra de progreso de distribución -->
            <div class="single-metric-bar">
                <div class="bar-fill estrato-123-bar" style="width: {porcentaje_123}%">
                    <span class="bar-label">1-3</span>
                </div>
                <div class="bar-fill estrato-456-bar" style="width: {porcentaje_456}%">
                    <span class="bar-label">4-6</span>
                </div>
            </div>
            
            <!-- Información contextual pequeña -->
            <div class="single-metric-footer">
                <div class="footer-info">
                    <span>📋 Presupuesto Total: {format_currency(metrics['total_presupuesto'])}</span>
                    <span>💰 Disponible: {format_currency(metrics['total_restante'])}</span>
                    <span>🏘️ Comunas Activas: {metrics['total_comunas']}</span>
                </div>
            </div>
        </div>
    </div>
    """
    
    # Renderizar el HTML CORRECTAMENTE
    st.markdown(html_content, unsafe_allow_html=True)

# Mantener la función de comuna si la usas
def render_comuna_metrics(df_comuna):
    """Renderizar métricas específicas de una comuna"""
    if df_comuna.empty:
        return
    
    presupuesto = df_comuna['presupuesto_comuna'].sum()
    restante = df_comuna['restante_presupuesto_comuna'].sum()
    usuarios = df_comuna['numero_usuarios_comuna'].sum()
    fiducias = df_comuna['idfiducia'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Presupuesto Total", format_currency(presupuesto))
    
    with col2:
        porcentaje_restante = (restante / presupuesto * 100) if presupuesto > 0 else 0
        st.metric("Presupuesto Restante", format_currency(restante), f"{porcentaje_restante:.1f}%")
    
    with col3:
        st.metric("Usuarios Legalizados", f"{usuarios:,.0f}")
    
    with col4:
        st.metric("Fiducias", fiducias)