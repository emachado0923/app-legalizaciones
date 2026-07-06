"""Paquete de configuración global de la aplicación.

Expone los objetos `settings`, las constantes de tema (`SAPIENCIA_COLORS`,
`inject_global_css`) y los catálogos de fondos y comunas.
"""

from app.config.settings import (
    settings,
    APP_CONFIG,
    DB_CONFIG,
    COMUNA_MAPPING,
    CONFIGURACION_ESTRATOS_FONDOS,
    OPCIONES_FILTRO_FONDOS,
    MAPEO_FILTRO_A_FONDOS,
    # CORRECCIÓN V2
    MAPA_COMUNAS_ESPECIALES,
    CUPOS_APROXIMADOS,
    normalizar_nombre_comuna,
    obtener_cupos_aprox,
)
from app.config.theme import SAPIENCIA_COLORS, inject_global_css

__all__ = [
    "settings",
    "APP_CONFIG",
    "DB_CONFIG",
    "COMUNA_MAPPING",
    "CONFIGURACION_ESTRATOS_FONDOS",
    "OPCIONES_FILTRO_FONDOS",
    "MAPEO_FILTRO_A_FONDOS",
    "MAPA_COMUNAS_ESPECIALES",
    "CUPOS_APROXIMADOS",
    "normalizar_nombre_comuna",
    "obtener_cupos_aprox",
    "SAPIENCIA_COLORS",
    "inject_global_css",
]
