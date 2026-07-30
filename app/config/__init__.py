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
    # V6.12: fondo ENLAZA MUNDOS
    MAPA_ID_COMUNA,
    PREFIJOS_ENLAZA_MUNDOS,
    # V6.14: cupos por fondo+fuente+comuna
    CUPOS_RO,
    CUPOS_PP_EXTENDIENDO_FRONTERAS,
    CUPOS_PP_ENLAZA_MUNDOS,
    resolver_cupos,
    # V8: preseleccionados por fondo+fuente+comuna
    PRESELECCIONADOS_PP_PREGRADO,
    PRESELECCIONADOS_PP_EXTENDIENDO_FRONTERAS,
    PRESELECCIONADOS_PP_ENLAZA_MUNDOS,
    PRESELECCIONADOS_FONDO_UNICO,
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
    "MAPA_ID_COMUNA",
    "PREFIJOS_ENLAZA_MUNDOS",
    "CUPOS_RO",
    "CUPOS_PP_EXTENDIENDO_FRONTERAS",
    "CUPOS_PP_ENLAZA_MUNDOS",
    "resolver_cupos",
    "PRESELECCIONADOS_PP_PREGRADO",
    "PRESELECCIONADOS_PP_EXTENDIENDO_FRONTERAS",
    "PRESELECCIONADOS_PP_ENLAZA_MUNDOS",
    "PRESELECCIONADOS_FONDO_UNICO",
    "SAPIENCIA_COLORS",
    "inject_global_css",
]
