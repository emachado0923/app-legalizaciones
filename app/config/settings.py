"""Configuración global de la aplicación.

Centraliza:
- Lectura de variables de entorno (.env / `st.secrets` / `os.environ`).
- Constantes de la aplicación (título, periodo, TTL de caché).
- Catálogo de comunas y configuración de estratos por fondo.

Política de credenciales (comportamiento original restaurado):
- Todas las variables de BD tienen defaults hardcodeados apuntando a
  producción, así el despliegue en Cloud Run funciona sin configurar
  variables de entorno adicionales.
- Para desarrollo local, sobreescribir en `.env` (no commiteado).
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv

# Cargar .env si existe (en local). En Cloud Run las variables vienen del servicio.
load_dotenv()


def _get_secret(key: str, default: str | None = None) -> str | None:
    """Obtiene un secreto desde `st.secrets` o variables de entorno.

    Streamlit puede no estar disponible al importar (p.ej. tests),
    por eso el import es perezoso y silencia errores.
    """
    try:
        import streamlit as st  # import perezoso

        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        # SUPUESTO: si st.secrets no está disponible, caemos a os.getenv sin alertar.
        pass
    return os.getenv(key, default)


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Configuración de la aplicación
# ---------------------------------------------------------------------------
class Settings:
    """Configuración centralizada de la aplicación."""

    # Base de datos — defaults apuntan a producción (Cloud Run + VPC).
    # Para dev local, sobreescribir vía `.env`.
    DB_HOST: str = _get_secret("DB_HOST", "10.124.80.4") or "10.124.80.4"
    DB_PORT: int = int(_get_secret("DB_PORT", "3306") or 3306)
    DB_NAME: str = _get_secret("DB_NAME", "convocatoria_sapiencia") or "convocatoria_sapiencia"
    DB_USER: str = _get_secret("DB_USER", "julian.usuga") or "julian.usuga"
    DB_PASSWORD: str = _get_secret("DB_PASSWORD", "bhcL14K&~y&<dfo*") or "bhcL14K&~y&<dfo*"

    # Aplicación
    APP_TITLE: str = "Dashboard Fiducias - Sapiencia"
    APP_ICON: str = "📊"
    PAGE_LAYOUT: str = "wide"
    APP_VERSION: str = "2.0.0"

    # Tablas y vistas
    TABLE_PRESUPUESTO: str = "callg_control_presupuesto_comuna_fidu"
    VISTA_CITAS: str = "vw_callg_control_citas_con_historico"

    # Negocio
    CURRENT_PERIOD: int = int(_get_secret("CURRENT_PERIOD", "16") or 16)
    CACHE_TTL: int = int(_get_secret("CACHE_TTL", "300") or 300)

    # Debug
    DEBUG: bool = (_get_secret("DEBUG", "false") or "false").lower() == "true"


settings = Settings()


# ---------------------------------------------------------------------------
# Backward-compat: dict APP_CONFIG / DB_CONFIG usados por módulos legacy
# ---------------------------------------------------------------------------
APP_CONFIG: Dict[str, Any] = {
    "page_title": settings.APP_TITLE,
    "page_icon": settings.APP_ICON,
    "layout": settings.PAGE_LAYOUT,
    "table_name": settings.TABLE_PRESUPUESTO,
    "current_period": settings.CURRENT_PERIOD,
    "cache_ttl": settings.CACHE_TTL,
}

DB_CONFIG: Dict[str, Any] = {
    "host": settings.DB_HOST,
    "database": settings.DB_NAME,
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "port": settings.DB_PORT,
}


# ---------------------------------------------------------------------------
# Catálogo de comunas
# ---------------------------------------------------------------------------
COMUNA_MAPPING: Dict[str, str] = {
    "90456": "90 - SANTA ELENA",
    "16456": "16 - BELEN",
    "15456": "15 - GUAYABAL",
    "14456": "14 - POBLADO",
    "12456": "12 - LA AMERICA",
    "11456": "11 - LAURELES/ESTADIO",
    "10456": "10 - LA CANDELARIA",
    "9456": "09 - BUENOS AIRES",
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
    "1123": "01 - POPULAR",
    "100234": "RECURSO ORDINARIO",
}


# ---------------------------------------------------------------------------
# Configuración de tarjetas dinámicas por fondo / línea (Fase 4)
# ---------------------------------------------------------------------------
# La columna en BD puede llamarse `fuente_financiacion` (tabla presupuestos)
# o `linea` (vista de citas). Aquí indexamos por el valor textual que aparece
# en `fuente_financiacion`.
CONFIGURACION_ESTRATOS_FONDOS: Dict[str, Dict[str, Any]] = {
    # LÍNEA PREGRADO
    "PRESUPUESTO PARTICIPATIVO": {
        "tipo": "pregrado",
        "tarjetas": [
            {"label": "Estratos 1 - 3", "estratos": [1, 2, 3]},
            {"label": "Estratos 4 - 6", "estratos": [4, 5, 6]},
        ],
    },
    "RECURSO ORDINARIO": {
        "tipo": "pregrado",
        "tarjetas": [
            {"label": "Estratos 1 - 4", "estratos": [1, 2, 3, 4]},
        ],
    },
    # MEJORES DEPORTISTAS
    "MEJORES DEPORTISTAS": {
        "tipo": "pregrado_especial",
        "tarjetas": [
            {"label": "Estratos 1 - 6", "estratos": [1, 2, 3, 4, 5, 6]},
        ],
    },
    # FORMACIÓN AVANZADA — Posgrados Maestros (identificador comuna: 219456)
    "FORMACION AVANZADA": {
        "tipo": "posgrado",
        "identificador_comuna": "219456",
        "tarjetas": [
            {"label": "Estratos 1 - 6", "estratos": [1, 2, 3, 4, 5, 6]},
        ],
    },
    # EXTENDIENDO FRONTERAS — Posgrados Nacionales
    "EXTENDIENDO FRONTERAS - RECURSO ORDINARIO": {
        "tipo": "posgrado",
        "identificador_comuna": "220456",
        "tarjetas": [
            {"label": "Estratos 1 - 6", "estratos": [1, 2, 3, 4, 5, 6]},
        ],
    },
    "EXTENDIENDO FRONTERAS - PRESUPUESTO PARTICIPATIVO": {
        "tipo": "posgrado",
        # Mapeo por comuna (16 comunas de Medellín)
        "identificador_comuna": {
            "1 - POPULAR": "2204561",
            "2 - SANTA CRUZ": "2204562",
            "3 - MANRIQUE": "2204563",
            "4 - ARANJUEZ": "2204564",
            "5 - CASTILLA": "2204565",
            "6 - DOCE DE OCTUBRE": "2204566",
            "7 - ROBLEDO": "2204567",
            "8 - VILLA HERMOSA": "2204568",
            "9 - BUENOS AIRES": "2204569",
            "10 - LA CANDELARIA": "22045610",
            "11 - LAURELES": "22045611",
            "12 - LA AMERICA": "22045612",
            "13 - SAN JAVIER": "22045613",
            "14 - POBLADO": "22045614",
            "15 - GUAYABAL": "22045615",
            "16 - BELEN": "22045616",
        },
        "tarjetas": [
            {"label": "Estratos 1 - 6", "estratos": [1, 2, 3, 4, 5, 6]},
        ],
    },
    # V6.12: ENLAZA MUNDOS RO — 4 modalidades (Pasantía / Doble Titulación / Doctorado / Maestría)
    "ENLAZA MUNDOS - RECURSO ORDINARIO": {
        "tipo": "posgrado_internacional",
        "modalidades": {
            "2214561": "Pasantía",
            "2214562": "Doble Titulación",
            "2214563": "Doctorado",
            "2214564": "Maestría",
        },
        "tarjetas": [
            {"label": "Estratos 1 - 6", "estratos": [1, 2, 3, 4, 5, 6]},
        ],
    },
    # V7: CDJ — Consejeros Distritales de Juventudes (identificador comuna: 100237)
    "CONSEJEROS DISTRITALES DE JUVENTUDES": {
        "tipo": "especial",
        "modalidades": ["Pregrado", "Posgrado"],
        "identificador_comuna": "100237",
        "tarjetas": [
            {"label": "Estratos 1 - 6", "estratos": [1, 2, 3, 4, 5, 6]},
        ],
    },
    # V6.12: ENLAZA MUNDOS PP — códigos = [prefijo_modalidad][id_comuna]
    "ENLAZA MUNDOS - PRESUPUESTO PARTICIPATIVO": {
        "tipo": "posgrado_internacional",
        "comunas_priorizan": [
            "4 - ARANJUEZ",
            "7 - ROBLEDO",
            "13 - SAN JAVIER",
            "16 - BELEN",
            "50 - SAN SEBASTIAN DE PALMITAS",
            "80 - SAN ANTONIO DE PRADO",
            "90 - SANTA ELENA",
        ],
        "modalidades": {
            "2214561": "Pasantía",
            "2214562": "Doble Titulación",
            "2214563": "Doctorado",
            "2214564": "Maestría",
        },
        "tarjetas": [
            {"label": "Estratos 1 - 6", "estratos": [1, 2, 3, 4, 5, 6]},
        ],
    },
}


# ---------------------------------------------------------------------------
# Opciones de filtro mostradas al usuario
# ---------------------------------------------------------------------------
OPCIONES_FILTRO_FONDOS: List[str] = [
    "LÍNEA PREGRADO",
    "FORMACIÓN AVANZADA",
    "EXTENDIENDO FRONTERAS",
    "MEJORES DEPORTISTAS",
    "ENLAZA MUNDOS",  # V6.12
    "CDJ",  # V7
]

# Cada opción del multiselect se traduce a una lista de valores reales de
# `fuente_financiacion` que viven en la BD.
MAPEO_FILTRO_A_FONDOS: Dict[str, List[str]] = {
    # LÍNEA PREGRADO agrupa los dos fondos cuyo `tipo == "pregrado"`.
    "LÍNEA PREGRADO": ["RECURSO ORDINARIO", "PRESUPUESTO PARTICIPATIVO"],
    "FORMACIÓN AVANZADA": ["FORMACION AVANZADA"],
    "EXTENDIENDO FRONTERAS": [
        "EXTENDIENDO FRONTERAS - RECURSO ORDINARIO",
        "EXTENDIENDO FRONTERAS - PRESUPUESTO PARTICIPATIVO",
    ],
    "MEJORES DEPORTISTAS": ["MEJORES DEPORTISTAS"],
    # V6.12: ENLAZA MUNDOS agrupa RO + PP
    "ENLAZA MUNDOS": [
        "ENLAZA MUNDOS - RECURSO ORDINARIO",
        "ENLAZA MUNDOS - PRESUPUESTO PARTICIPATIVO",
    ],
    # V7: CDJ — un único fondo (código 100237, sin RO/PP)
    "CDJ": ["CONSEJEROS DISTRITALES DE JUVENTUDES"],
}


# ---------------------------------------------------------------------------
# CORRECCIÓN V2: Mapeo de identificadores especiales de comuna a nombre legible
# ---------------------------------------------------------------------------
# Los códigos numéricos largos en la columna `comuna` no son comunas reales:
# corresponden a fondos de posgrado y a EXTENDIENDO FRONTERAS - PP por comuna.
# Sin este mapa la tabla mostraría literalmente "Comuna 219456".
MAPA_COMUNAS_ESPECIALES: Dict[str, str] = {
    "219456": "FORMACIÓN AVANZADA",
    "220456": "EXTENDIENDO FRONTERAS (RO)",
    "2204561": "1 - POPULAR (EFE)",
    "2204562": "2 - SANTA CRUZ (EFE)",
    "2204563": "3 - MANRIQUE (EFE)",
    "2204564": "4 - ARANJUEZ (EFE)",
    "2204565": "5 - CASTILLA (EFE)",
    "2204566": "6 - DOCE DE OCTUBRE (EFE)",
    "2204567": "7 - ROBLEDO (EFE)",
    "2204568": "8 - VILLA HERMOSA (EFE)",
    "2204569": "9 - BUENOS AIRES (EFE)",
    "22045610": "10 - LA CANDELARIA (EFE)",
    "22045611": "11 - LAURELES (EFE)",
    "22045612": "12 - LA AMERICA (EFE)",
    "22045613": "13 - SAN JAVIER (EFE)",
    "22045614": "14 - POBLADO (EFE)",
    "22045615": "15 - GUAYABAL (EFE)",
    "22045616": "16 - BELÉN (EFE)",
    # SUPUESTO: los códigos 22045650..22045690 corresponden a los corregimientos
    # 50/60/70/80/90 (no estaban en el spec original pero existen en la BD).
    "22045650": "50 - SAN SEBASTIAN DE PALMITAS (EFE)",
    "22045660": "60 - SAN CRISTOBAL (EFE)",
    "22045670": "70 - ALTAVISTA (EFE)",
    "22045680": "80 - SAN ANTONIO DE PRADO (EFE)",
    "22045690": "90 - SANTA ELENA (EFE)",
    # MEJORES DEPORTISTAS también tiene su propio código
    "100235": "MEJORES DEPORTISTAS",
    # V7: CDJ — Consejeros Distritales de Juventudes
    "100237": "CDJ - Consejeros Distritales de Juventudes",
    # V6.12: ENLAZA MUNDOS RO — 4 modalidades (códigos base sin id_comuna)
    "2214561": "ENLAZA MUNDOS - Pasantía (RO)",
    "2214562": "ENLAZA MUNDOS - Doble Titulación (RO)",
    "2214563": "ENLAZA MUNDOS - Doctorado (RO)",
    "2214564": "ENLAZA MUNDOS - Maestría (RO)",
}


# ---------------------------------------------------------------------------
# V6.12: Mapa id numérico → nombre de comuna legible
# Usado por normalizar_nombre_comuna() al reconocer el patrón
# ENLAZA MUNDOS PP: [prefijo_modalidad][id_comuna]
# ---------------------------------------------------------------------------
MAPA_ID_COMUNA: Dict[str, str] = {
    "1": "1 - POPULAR",
    "2": "2 - SANTA CRUZ",
    "3": "3 - MANRIQUE",
    "4": "4 - ARANJUEZ",
    "5": "5 - CASTILLA",
    "6": "6 - DOCE DE OCTUBRE",
    "7": "7 - ROBLEDO",
    "8": "8 - VILLA HERMOSA",
    "9": "9 - BUENOS AIRES",
    "10": "10 - LA CANDELARIA",
    "11": "11 - LAURELES/ESTADIO",
    "12": "12 - LA AMERICA",
    "13": "13 - SAN JAVIER",
    "14": "14 - POBLADO",
    "15": "15 - GUAYABAL",
    "16": "16 - BELEN",
    "50": "50 - SAN SEBASTIAN DE PALMITAS",
    "60": "60 - SAN CRISTOBAL",
    "70": "70 - ALTAVISTA",
    "80": "80 - SAN ANTONIO DE PRADO",
    "90": "90 - SANTA ELENA",
}


# ---------------------------------------------------------------------------
# V6.12: prefijos de modalidad de ENLAZA MUNDOS (RO usa el código completo,
# PP concatena `id_comuna` después del prefijo).
# ---------------------------------------------------------------------------
PREFIJOS_ENLAZA_MUNDOS: Dict[str, str] = {
    "2214561": "Pasantía",
    "2214562": "Doble Titulación",
    "2214563": "Doctorado",
    "2214564": "Maestría",
}


def normalizar_nombre_comuna(codigo_o_nombre: Any) -> str:
    """Devuelve el nombre legible de una comuna a partir de su código.

    - Si recibe un código presente en `MAPA_COMUNAS_ESPECIALES`, devuelve el
      nombre legible.
    - Si recibe un string que contiene un código numérico de 5+ dígitos
      (p.ej. "21 - Comuna 219456"), lo extrae y lo busca en el mapa.
    - Si no hay coincidencia, devuelve el valor original.
    """
    if codigo_o_nombre is None:
        return ""

    codigo = str(codigo_o_nombre).strip()
    if not codigo:
        return ""

    # 1. Coincidencia directa por código exacto
    if codigo in MAPA_COMUNAS_ESPECIALES:
        return MAPA_COMUNAS_ESPECIALES[codigo]

    # V6.12: ENLAZA MUNDOS PP — patrón `[prefijo_modalidad_7digitos][id_comuna]`
    # Ej: 22145614 → 2214561 (Pasantía) + 4 (Aranjuez)
    #     221456113 → 2214561 (Pasantía) + 13 (San Javier)
    match_em = re.match(r"^(221456\d)(\d+)$", codigo)
    if match_em:
        prefijo = match_em.group(1)
        id_comuna = match_em.group(2)
        modalidad = PREFIJOS_ENLAZA_MUNDOS.get(prefijo, "Enlaza Mundos")
        nombre_com = MAPA_ID_COMUNA.get(id_comuna, f"Comuna {id_comuna}")
        return f"{nombre_com} - EM {modalidad} (PP)"

    # 2. Extraer número de 5+ dígitos del texto
    match = re.search(r"(\d{5,})", codigo)
    if match:
        codigo_extraido = match.group(1)
        if codigo_extraido in MAPA_COMUNAS_ESPECIALES:
            return MAPA_COMUNAS_ESPECIALES[codigo_extraido]

    return str(codigo_o_nombre)


# ---------------------------------------------------------------------------
# CORRECCIÓN V2: Cupos aproximados por comuna y rango de estrato
# ---------------------------------------------------------------------------
# Restaurado desde la versión original del overview (refactor V1 lo eliminó).
# La BD no expone esta información, por eso vive como dato de configuración.
# Comunas no listadas o fondos no contemplados → cupos = 0.
CUPOS_APROXIMADOS: Dict[str, Dict[str, Any]] = {
    "01 - POPULAR": {"1-3": 16, "4-6": "N.A"},
    "02 - SANTA CRUZ": {"1-3": 18, "4-6": "N.A"},
    "03 - MANRIQUE": {"1-3": 17, "4-6": "N.A"},
    "04 - ARANJUEZ": {"1-3": 20, "4-6": "N.A"},
    "05 - CASTILLA": {"1-3": 18, "4-6": "N.A"},
    "06 - DOCE DE OCTUBRE": {"1-3": 15, "4-6": "N.A"},
    "07 - ROBLEDO": {"1-3": 22, "4-6": 7},
    "08 - VILLA HERMOSA": {"1-3": 16, "4-6": 9},
    "09 - BUENOS AIRES": {"1-3": 19, "4-6": 4},
    "10 - LA CANDELARIA": {"1-3": 14, "4-6": 9},
    "11 - LAURELES/ESTADIO": {"1-3": 2, "4-6": 12},
    "12 - LA AMERICA": {"1-3": 9, "4-6": 10},
    "13 - SAN JAVIER": {"1-3": 23, "4-6": "N.A"},
    "14 - POBLADO": {"1-3": 12, "4-6": 17},
    "15 - GUAYABAL": {"1-3": 11, "4-6": 7},
    "16 - BELEN": {"1-3": 28, "4-6": 13},
    "50 - SAN SEBASTIAN DE PALMITAS": {"1-3": 14, "4-6": "N.A"},
    "60 - SAN CRISTOBAL": {"1-3": 18, "4-6": "N.A"},
    "70 - ALTAVISTA": {"1-3": 8, "4-6": "N.A"},
    "80 - SAN ANTONIO DE PRADO": {"1-3": 38, "4-6": "N.A"},
    "90 - SANTA ELENA": {"1-3": 17, "4-6": 2},
    "RECURSO ORDINARIO": {"1-4": 305}
    
}


def obtener_cupos_aprox(comuna_con_numero: Any, rango: Any) -> int:
    """Devuelve los cupos aproximados de una comuna y rango (entero o 0).

    Si el rango es "N.A" o no hay coincidencia, retorna 0.
    """
    if not comuna_con_numero or not rango:
        return 0

    clave = str(comuna_con_numero).strip()
    rango_str = str(rango).strip()

    # Quitar prefijos tipo " (Estrato X)"
    if " (Estrato" in clave:
        clave = clave.split(" (Estrato")[0].strip()

    valor = CUPOS_APROXIMADOS.get(clave, {}).get(rango_str)
    if valor is None or valor == "N.A":
        return 0
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0


# ---------------------------------------------------------------------------
# V6.14: Cupos aproximados por fondo+fuente+comuna (convocatoria 2026-2)
# ---------------------------------------------------------------------------
CUPOS_RO: Dict[str, int] = {
    "EXTENDIENDO FRONTERAS": 50,
    "ENLAZA MUNDOS": 50,
    "FORMACION AVANZADA": 50,
    "MEJORES DEPORTISTAS": 40,
    "LINEA PREGRADO RO": 301,
    "CDJ": 4,  # V7
}

CUPOS_PP_EXTENDIENDO_FRONTERAS: Dict[str, int] = {
    "1 - POPULAR": 11,
    "2 - SANTA CRUZ": 12,
    "3 - MANRIQUE": 0,
    "4 - ARANJUEZ": 14,
    "5 - CASTILLA": 11,
    "6 - DOCE DE OCTUBRE": 11,
    "7 - ROBLEDO": 12,
    "8 - VILLA HERMOSA": 11,
    "9 - BUENOS AIRES": 11,
    "10 - LA CANDELARIA": 11,
    # V9.1: alinear claves con lo que devuelve normalizar_nombre_comuna()
    # para códigos EFE PP: "11 - LAURELES (EFE)" y "16 - BELÉN (EFE)".
    "11 - LAURELES": 12,
    "12 - LA AMERICA": 11,
    "13 - SAN JAVIER": 11,
    "14 - POBLADO": 11,
    "15 - GUAYABAL": 4,
    "16 - BELÉN": 13,
    "50 - SAN SEBASTIAN DE PALMITAS": 14,
    "60 - SAN CRISTOBAL": 11,
    "70 - ALTAVISTA": 17,
    "80 - SAN ANTONIO DE PRADO": 11,
    "90 - SANTA ELENA": 20,
}

CUPOS_PP_ENLAZA_MUNDOS: Dict[str, int] = {
    "1 - POPULAR": 0,
    "2 - SANTA CRUZ": 0,
    "3 - MANRIQUE": 0,
    "4 - ARANJUEZ": 7,
    "5 - CASTILLA": 0,
    "6 - DOCE DE OCTUBRE": 0,
    "7 - ROBLEDO": 2,
    "8 - VILLA HERMOSA": 0,
    "9 - BUENOS AIRES": 0,
    "10 - LA CANDELARIA": 0,
    "11 - LAURELES/ESTADIO": 0,
    "12 - LA AMERICA": 0,
    "13 - SAN JAVIER": 10,
    "14 - POBLADO": 0,
    "15 - GUAYABAL": 0,
    "16 - BELEN": 5,
    "50 - SAN SEBASTIAN DE PALMITAS": 5,
    "60 - SAN CRISTOBAL": 0,
    "70 - ALTAVISTA": 0,
    "80 - SAN ANTONIO DE PRADO": 22,
    "90 - SANTA ELENA": 5,
}


# ---------------------------------------------------------------------------
# V8: Preseleccionados por fondo, fuente y comuna
# ---------------------------------------------------------------------------
# V9.1: Reemplaza el dict plano por uno diferenciado por grupo estrato.
PRESELECCIONADOS_PP_PREGRADO_POR_ESTRATO: Dict[str, Dict[str, int]] = {
    "1 - POPULAR": {"1-3": 74, "4-6": 0},
    "2 - SANTA CRUZ": {"1-3": 77, "4-6": 0},
    "3 - MANRIQUE": {"1-3": 94, "4-6": 0},
    "4 - ARANJUEZ": {"1-3": 81, "4-6": 0},
    "5 - CASTILLA": {"1-3": 74, "4-6": 0},
    "6 - DOCE DE OCTUBRE": {"1-3": 73, "4-6": 0},
    "7 - ROBLEDO": {"1-3": 97, "4-6": 16},
    "8 - VILLA HERMOSA": {"1-3": 71, "4-6": 9},
    "9 - BUENOS AIRES": {"1-3": 85, "4-6": 13},
    "10 - LA CANDELARIA": {"1-3": 41, "4-6": 26},
    "11 - LAURELES/ESTADIO": {"1-3": 5, "4-6": 36},
    "12 - LA AMERICA": {"1-3": 41, "4-6": 31},
    "13 - SAN JAVIER": {"1-3": 89, "4-6": 0},
    "14 - POBLADO": {"1-3": 35, "4-6": 37},
    "15 - GUAYABAL": {"1-3": 40, "4-6": 18},
    "16 - BELEN": {"1-3": 119, "4-6": 34},
    "50 - SAN SEBASTIAN DE PALMITAS": {"1-3": 18, "4-6": 0},
    "60 - SAN CRISTOBAL": {"1-3": 78, "4-6": 0},
    "70 - ALTAVISTA": {"1-3": 40, "4-6": 0},
    "80 - SAN ANTONIO DE PRADO": {"1-3": 139, "4-6": 0},
    "90 - SANTA ELENA": {"1-3": 59, "4-6": 1},
}

PRESELECCIONADOS_PP_EXTENDIENDO_FRONTERAS: Dict[str, int] = {
    "1 - POPULAR": 19,
    "2 - SANTA CRUZ": 25,
    "4 - ARANJUEZ": 28,
    "5 - CASTILLA": 23,
    "6 - DOCE DE OCTUBRE": 17,
    "7 - ROBLEDO": 45,
    "8 - VILLA HERMOSA": 20,
    "9 - BUENOS AIRES": 26,
    "10 - LA CANDELARIA": 25,
    # V9.1: alinear con nombre_base normalizado (sin /ESTADIO, con tilde en BELÉN)
    "11 - LAURELES": 33,
    "12 - LA AMERICA": 21,
    "13 - SAN JAVIER": 28,
    "14 - POBLADO": 23,
    "15 - GUAYABAL": 8,
    "16 - BELÉN": 33,
    "50 - SAN SEBASTIAN DE PALMITAS": 4,
    "60 - SAN CRISTOBAL": 26,
    "70 - ALTAVISTA": 15,
    "80 - SAN ANTONIO DE PRADO": 24,
    "90 - SANTA ELENA": 19,
}

PRESELECCIONADOS_PP_ENLAZA_MUNDOS: Dict[str, int] = {
    "4 - ARANJUEZ": 5,
    "7 - ROBLEDO": 10,
    "13 - SAN JAVIER": 6,
    "14 - POBLADO": 1,
    "16 - BELEN": 9,
}

PRESELECCIONADOS_FONDO_UNICO: Dict[str, int] = {
    "PREGRADO RO": 945,
    "EXTENDIENDO FRONTERAS RO": 84,
    "MEJORES DEPORTISTAS": 11,
    "FORMACION AVANZADA": 76,
    "CDJ": 4,
    "ENLAZA MUNDOS RO": 75,
}


def resolver_cupos(fondo: Any, fuente: Any, comuna_normalizada: Any) -> int:
    """Devuelve los cupos aproximados para (fondo, fuente, comuna).

    - fondo: nombre del fondo (ej. "EXTENDIENDO FRONTERAS", "ENLAZA MUNDOS",
      "FORMACION AVANZADA", "MEJORES DEPORTISTAS", "PRESUPUESTO PARTICIPATIVO",
      "RECURSO ORDINARIO"). Puede venir con sufijos tipo " - RECURSO ORDINARIO".
    - fuente: "RECURSO ORDINARIO" | "PRESUPUESTO PARTICIPATIVO".
    - comuna_normalizada: nombre legible (ej. "07 - ROBLEDO", "4 - ARANJUEZ (EFE)").
      Se admite con o sin cero inicial en el número.
    Retorna 0 si no hay match.
    """
    if not fondo:
        return 0

    fondo_u = str(fondo).upper()
    fuente_u = str(fuente or "").upper()

    # V7: CDJ es un fondo especial (no aplica RO/PP tradicional); atender antes
    # del guard de `fuente` porque puede llegar sin valor de fuente.
    if "CDJ" in fondo_u or "CONSEJEROS DISTRITALES" in fondo_u:
        return CUPOS_RO.get("CDJ", 0)

    if not fuente_u:
        return 0

    if fuente_u == "RECURSO ORDINARIO":
        if "EXTENDIENDO FRONTERAS" in fondo_u:
            return CUPOS_RO.get("EXTENDIENDO FRONTERAS", 0)
        if "ENLAZA MUNDOS" in fondo_u:
            return CUPOS_RO.get("ENLAZA MUNDOS", 0)
        if "FORMACION AVANZADA" in fondo_u or "FORMACIÓN AVANZADA" in fondo_u:
            return CUPOS_RO.get("FORMACION AVANZADA", 0)
        if "MEJORES DEPORTISTAS" in fondo_u:
            return CUPOS_RO.get("MEJORES DEPORTISTAS", 0)
        # Pregrado RO (PUAP / LINEA PREGRADO)
        return CUPOS_RO.get("LINEA PREGRADO RO", 0)

    if fuente_u == "PRESUPUESTO PARTICIPATIVO":
        # Reducir a "N - NOMBRE" quitando cualquier sufijo (EFE, EM Pasantía, etc.)
        raw = str(comuna_normalizada or "").split(" (")[0].strip()
        partes = [p.strip() for p in raw.split(" - ") if p.strip()]
        if len(partes) >= 2:
            prefijo_num = partes[0].lstrip("0") or "0"
            # Aceptamos que el nombre pueda contener "/" o espacios (ej. LAURELES/ESTADIO)
            nombre_base = f"{prefijo_num} - {partes[1]}"
        else:
            nombre_base = raw
        if "EXTENDIENDO FRONTERAS" in fondo_u:
            return CUPOS_PP_EXTENDIENDO_FRONTERAS.get(nombre_base, 0)
        if "ENLAZA MUNDOS" in fondo_u:
            return CUPOS_PP_ENLAZA_MUNDOS.get(nombre_base, 0)

    return 0
