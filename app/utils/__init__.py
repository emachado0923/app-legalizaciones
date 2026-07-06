"""Paquete de utilidades transversales.

Reexporta funciones de formateo y validación para mantener imports cortos:
    from app.utils import format_currency, buscar_por_documento
"""

from app.utils.formatters import (
    format_currency,
    format_currency_short,
    format_number_integer,
    format_percentage,
    get_colombia_time,
    format_colombia_time,
    get_time_with_timezone,
    get_comuna_numero,
    format_comuna_con_numero,
    get_comunas_formateadas,
    # CORRECCIÓN V2
    etiquetar_grupo_estrato,
    calcular_legalizados_por_segmento,
    # CORRECCIÓN V3
    get_badge_estado,
    get_color_utilizacion,
    # CORRECCIÓN V4
    escapar_html,
    formatear_documento,
)
from app.utils.validators import (
    es_documento_valido,
    buscar_por_documento,
)
from app.utils.processors import (
    process_comuna_data,
    calculate_summary_metrics,
)

__all__ = [
    # formatters
    "format_currency",
    "format_currency_short",
    "format_number_integer",
    "format_percentage",
    "get_colombia_time",
    "format_colombia_time",
    "get_time_with_timezone",
    "get_comuna_numero",
    "format_comuna_con_numero",
    "get_comunas_formateadas",
    "etiquetar_grupo_estrato",
    "calcular_legalizados_por_segmento",
    "get_badge_estado",
    "get_color_utilizacion",
    "escapar_html",
    "formatear_documento",
    # validators
    "es_documento_valido",
    "buscar_por_documento",
    # processors
    "process_comuna_data",
    "calculate_summary_metrics",
]
