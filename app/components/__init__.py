"""Componentes visuales reutilizables del dashboard."""

from app.components.cards import (
    render_tarjetas_recurso_comunas,
    render_tarjetas_por_fondo,
    render_tarjeta_metrica,
    # CORRECCIÓN V2
    render_tarjeta_legalizados_segmento,
    # CORRECCIÓN V3
    render_tarjeta_estrato_con_fiducias,
    agrupar_para_resumen_estrato,
)
from app.components.header import render_header, render_control_bar
from app.components.tables import render_tabla_resumen_general

__all__ = [
    "render_header",
    "render_control_bar",
    "render_tarjetas_recurso_comunas",
    "render_tarjetas_por_fondo",
    "render_tarjeta_metrica",
    "render_tarjeta_legalizados_segmento",
    "render_tarjeta_estrato_con_fiducias",
    "agrupar_para_resumen_estrato",
    "render_tabla_resumen_general",
]
