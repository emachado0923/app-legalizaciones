# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de la aplicación
class Settings:
    # Base de datos
    DB_HOST = os.getenv("DB_HOST", "10.124.80.4")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_NAME = os.getenv("DB_NAME", "convocatoria_sapiencia")
    DB_USER = os.getenv("DB_USER", "julian.usuga")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "bhcL14K&~y&<dfo*")
    
    # Aplicación
    APP_TITLE = "Dashboard Fiducias - Sapiencia"
    APP_ICON = "💰"
    PAGE_LAYOUT = "wide"
    TABLE_NAME = "callg_control_presupuesto_comuna_fidu"
    CURRENT_PERIOD = 15
    CACHE_TTL = 60
    
    # Debug
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()
