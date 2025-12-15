# app/config.py
import os
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de base de datos (se puede sobrescribir con .env)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.124.80.4'),
    'database': os.getenv('DB_NAME', 'convocatoria_sapiencia'),
    'user': os.getenv('DB_USER', 'julian.usuga'),
    'password': os.getenv('DB_PASSWORD', 'bhcL14K&~y&<dfo*'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Mapeo de comunas
COMUNA_MAPPING = {
    "90456": "90 - SANTA ELENA",
    "16456": "16 - BELEN",
    "15456": "15 - GUAYABAL",
    "14456": "14 - POBLADO",
    "12456": "12 - LA AMERICA",
    "11456": "11 - LAURELES/ESTADIO",
    "10456": "10 - LA CANDELARIA",
    "8456": "08 - VILLA HERMOSA",
    "90123": "90 - SANTA ELENA",
    "80123": "80 - SAN ANTONIO DE PRADO",
    "70123": "70 - ALTAVISTA",
    "60123": "60 - SAN CRISTOBAL",
    "50123": "50 - SAN SEBASTIAN DE PALMITAS",
    "16123": "16 - BELEN",
    "15123": "15 - GUAYABAL",
    "14123": "14 - POBLADO",
    "13123": "13 - SAN JAVIER",
    "12123": "12 - LA AMERICA",
    "11123": "11 - LAURELES/ESTADIO",
    "10123": "10 - LA CANDELARIA",
    "9123": "09 - BUENOS AIRES",
    "8123": "08 - VILLA HERMOSA",
    "7123": "07 - ROBLEDO",
    "7456": "07 - ROBLEDO",
    "6123": "06 - DOCE DE OCTUBRE",
    "5123": "05 - CASTILLA",
    "4123": "04 - ARANJUEZ",
    "3123": "03 - MANRIQUE",
    "2123": "02 - SANTA CRUZ",
    "1123": "01 - POPULAR"
}

# Configuración de la aplicación
APP_CONFIG = {
    'page_title': 'Dashboard Fiducias - Sapiencia',
    'page_icon': '💰',
    'layout': 'wide',
    'table_name': 'callg_control_presupuesto_comuna_fidu',
    'current_period': 15,
    'cache_ttl': 60
}
