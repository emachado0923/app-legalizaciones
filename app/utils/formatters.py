"""Funciones de formateo: moneda, números, fechas, comunas."""
from __future__ import annotations

import html as _html_lib
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

import pandas as pd


# ---------------------------------------------------------------------------
# CORRECCIÓN V4: helpers de saneamiento y normalización
# ---------------------------------------------------------------------------
def escapar_html(texto: Any) -> str:
    """Escapa caracteres HTML peligrosos para interpolar valores en f-strings.

    Necesario porque al interpolar texto de la BD en `st.markdown(..., unsafe_allow_html=True)`,
    comillas o `<` no escapados pueden romper la estructura del HTML.
    """
    if texto is None:
        return ""
    return _html_lib.escape(str(texto), quote=True)


def formatear_documento(valor: Any) -> str:
    """Convierte un valor de documento (a veces `float` por NaN en MySQL) a string entero.

    Ejemplos: `1047044130.0` → `"1047044130"`, `None`/`NaN` → `""`, `" 43868272 "` → `"43868272"`.
    """
    if valor is None:
        return ""
    try:
        if pd.isna(valor):
            return ""
    except (TypeError, ValueError):
        pass
    try:
        return str(int(float(str(valor).strip())))
    except (ValueError, TypeError):
        return str(valor).strip()

# ---------------------------------------------------------------------------
# Catálogo de comunas (mapeo de nombre canónico a número)
# ---------------------------------------------------------------------------
COMUNA_NUMEROS: Dict[str, str] = {
    "POPULAR": "01",
    "SANTA CRUZ": "02",
    "MANRIQUE": "03",
    "ARANJUEZ": "04",
    "CASTILLA": "05",
    "DOCE DE OCTUBRE": "06",
    "ROBLEDO": "07",
    "VILLA HERMOSA": "08",
    "BUENOS AIRES": "09",
    "LA CANDELARIA": "10",
    "LAURELES/ESTADIO": "11",
    "LA AMERICA": "12",
    "SAN JAVIER": "13",
    "POBLADO": "14",
    "GUAYABAL": "15",
    "BELEN": "16",
    "SAN SEBASTIAN DE PALMITAS": "50",
    "SAN CRISTOBAL": "60",
    "ALTAVISTA": "70",
    "SAN ANTONIO DE PRADO": "80",
    "SANTA ELENA": "90",
}


# ---------------------------------------------------------------------------
# Formateo de moneda
# ---------------------------------------------------------------------------
def format_currency(value: Any) -> str:
    """Formatea un valor numérico como pesos colombianos: `$ 1,234,567`.

    Sin abreviaturas, separador de miles con coma. Si el valor es NaN o
    inválido retorna `"$ 0"`.
    """
    if pd.isna(value) or value is None:
        return "$ 0"
    try:
        valor_int = int(float(value))
        return f"$ {valor_int:,}"
    except (ValueError, TypeError):
        return "$ 0"


def format_currency_short(value: Any) -> str:
    """Formatea moneda con abreviatura (K/M/B) para espacios reducidos."""
    if pd.isna(value) or value is None:
        return "$ 0"
    try:
        valor = float(value)
        if valor >= 1e9:
            return f"$ {valor / 1e9:,.2f}B"
        if valor >= 1e6:
            return f"$ {valor / 1e6:,.2f}M"
        if valor >= 1e3:
            return f"$ {valor / 1e3:,.1f}K"
        return f"$ {valor:,.0f}"
    except (ValueError, TypeError):
        return "$ 0"


def format_number_integer(value: Any) -> str:
    """Formatea como entero con separador de miles. NaN → `"0"`."""
    if pd.isna(value) or value is None:
        return "0"
    try:
        return f"{int(float(value)):,}"
    except (ValueError, TypeError):
        return "0"


def format_percentage(value: Any, decimals: int = 1) -> str:
    """Formatea un porcentaje con N decimales. NaN → `"0.0%"`."""
    if pd.isna(value) or value is None:
        return f"{0:.{decimals}f}%"
    try:
        return f"{float(value):.{decimals}f}%"
    except (ValueError, TypeError):
        return f"{0:.{decimals}f}%"


# ---------------------------------------------------------------------------
# Fechas en zona horaria Colombia (UTC-5, sin horario de verano)
# ---------------------------------------------------------------------------
_COLOMBIA_TZ = timezone(timedelta(hours=-5))


def get_colombia_time() -> datetime:
    """Retorna la hora actual en zona Colombia (UTC-5), naive."""
    return datetime.now(_COLOMBIA_TZ).replace(tzinfo=None)


def format_colombia_time(
    datetime_obj: datetime | None = None,
    formato: str = "%d/%m/%Y %I:%M %p",
) -> str:
    """Formatea un datetime en zona Colombia. Si es None usa la hora actual."""
    if datetime_obj is None:
        datetime_obj = get_colombia_time()
    return datetime_obj.strftime(formato)


def get_time_with_timezone() -> str:
    """Hora actual Colombia con sufijo descriptivo."""
    return f"{format_colombia_time()} (Hora Colombia)"


# ---------------------------------------------------------------------------
# Helpers de comunas
# ---------------------------------------------------------------------------
def get_comuna_numero(comuna_nombre: Any) -> str:
    """Obtiene el número de comuna a partir del nombre."""
    if not comuna_nombre or pd.isna(comuna_nombre):
        return "00"

    comuna_upper = str(comuna_nombre).upper().strip()
    for nombre, numero in COMUNA_NUMEROS.items():
        if nombre in comuna_upper or comuna_upper in nombre:
            return numero
    match = re.search(r"(\d{2})", comuna_upper)
    return match.group(1) if match else "00"


def format_comuna_con_numero(comuna_nombre: Any) -> str:
    """Formatea como `"NN - NOMBRE"`. Para `"TODAS LAS COMUNAS"` la deja igual."""
    if not comuna_nombre or comuna_nombre == "TODAS LAS COMUNAS":
        return str(comuna_nombre) if comuna_nombre else ""

    numero = get_comuna_numero(comuna_nombre)
    return f"{numero} - {comuna_nombre}"


# ---------------------------------------------------------------------------
# CORRECCIÓN V3: badge y color de utilización (5 niveles)
# ---------------------------------------------------------------------------
def get_badge_estado(pct_utilizacion: Any) -> Dict[str, str]:
    """Etiqueta y colores del badge según porcentaje de utilización.

    Buckets:
    - <30%  → MUY DISPONIBLE (verde oscuro)
    - <60%  → DISPONIBLE      (verde medio)
    - <80%  → MODERADO        (ámbar)
    - <95%  → ALTO USO        (naranja)
    - ≥95%  → CRÍTICO         (rojo)
    """
    try:
        pct = float(pct_utilizacion) if pct_utilizacion is not None else 0.0
        if pd.isna(pct):
            pct = 0.0
    except (ValueError, TypeError):
        pct = 0.0

    if pct < 30:
        return {"label": "MUY DISPONIBLE", "bg": "#2E7D32", "text": "#FFFFFF"}
    if pct < 60:
        return {"label": "DISPONIBLE", "bg": "#558B2F", "text": "#FFFFFF"}
    if pct < 80:
        return {"label": "MODERADO", "bg": "#F57F17", "text": "#FFFFFF"}
    if pct < 95:
        return {"label": "ALTO USO", "bg": "#E65100", "text": "#FFFFFF"}
    return {"label": "CRÍTICO", "bg": "#C62828", "text": "#FFFFFF"}


def get_color_utilizacion(pct: Any) -> str:
    """Color del texto y barra de progreso según porcentaje de utilización."""
    try:
        valor = float(pct) if pct is not None else 0.0
        if pd.isna(valor):
            valor = 0.0
    except (ValueError, TypeError):
        valor = 0.0

    if valor < 30:
        return "#2E7D32"
    if valor < 60:
        return "#558B2F"
    if valor < 80:
        return "#F57F17"
    if valor < 95:
        return "#E65100"
    return "#C62828"


# ---------------------------------------------------------------------------
# CORRECCIÓN V2: etiqueta de grupo estrato según fuente de financiación
# ---------------------------------------------------------------------------
def etiquetar_grupo_estrato(fuente: Any, estratos_raw: Any) -> str:
    """Etiqueta correcta del grupo de estrato según la fuente de financiación.

    - RECURSO ORDINARIO (pregrado): máximo estrato 4 → "1-4".
    - Posgrados (FORMACION AVANZADA, EXTENDIENDO FRONTERAS, MEJORES
      DEPORTISTAS): cubren todos → "1-6".
    - PRESUPUESTO PARTICIPATIVO (pregrado): respeta el valor del dato
      ("1-3" o "4-6").
    """
    if fuente is None or pd.isna(fuente):
        return str(estratos_raw) if estratos_raw is not None and not pd.isna(estratos_raw) else "-"

    fuente_upper = str(fuente).strip().upper()

    if fuente_upper == "RECURSO ORDINARIO":
        return "1-4"

    # Posgrados y especiales cubren todo el rango
    if (
        fuente_upper == "FORMACION AVANZADA"
        or fuente_upper == "FORMACIÓN AVANZADA"
        or fuente_upper.startswith("EXTENDIENDO FRONTERAS")
        or fuente_upper == "MEJORES DEPORTISTAS"
    ):
        return "1-6"

    # PRESUPUESTO PARTICIPATIVO: respetar el dato
    if estratos_raw is None or pd.isna(estratos_raw):
        return "-"
    return str(estratos_raw)


# ---------------------------------------------------------------------------
# CORRECCIÓN V2: conteo de legalizados por segmento configurable
# ---------------------------------------------------------------------------
def calcular_legalizados_por_segmento(df: pd.DataFrame, clave_filtro: Dict[str, Any]) -> int:
    """Cuenta usuarios legalizados de un segmento definido por filtros.

    Acepta combinaciones de claves:
    - `fuente`: valor base de PRESUPUESTO PARTICIPATIVO / RECURSO ORDINARIO.
    - `fondo`: distingue entre LÍNEA PREGRADO y EXTENDIENDO FRONTERAS / FA / MD.
    - `tipo`: 'pregrado' / 'posgrado' / 'pregrado_especial' (validación lógica).
    - `estrato_grupo`: '1-3' / '4-6' / '1-4' / '1-6'.

    Retorna el conteo (entero). Si no hay datos, retorna 0.
    """
    if df is None or df.empty or "numero_usuarios_comuna" not in df.columns:
        return 0

    fondo = clave_filtro.get("fondo")
    fuente = clave_filtro.get("fuente")
    estrato_grupo = clave_filtro.get("estrato_grupo")

    if "fuente_financiacion" not in df.columns:
        return 0

    sub = df.copy()

    # Resolver `fuente_financiacion` real a partir de fondo + fuente
    if fondo == "EXTENDIENDO FRONTERAS":
        valor_fuente_fin = (
            f"EXTENDIENDO FRONTERAS - {str(fuente).upper()}" if fuente else None
        )
        if valor_fuente_fin:
            sub = sub[sub["fuente_financiacion"] == valor_fuente_fin]
        else:
            sub = sub[sub["fuente_financiacion"].str.startswith("EXTENDIENDO FRONTERAS", na=False)]
    elif fondo == "FORMACION AVANZADA" or fondo == "FORMACIÓN AVANZADA":
        sub = sub[sub["fuente_financiacion"].isin(["FORMACION AVANZADA", "FORMACIÓN AVANZADA"])]
    elif fondo == "MEJORES DEPORTISTAS":
        sub = sub[sub["fuente_financiacion"] == "MEJORES DEPORTISTAS"]
    elif fuente:
        # Sin `fondo`: filtro por la fuente directa (pregrado RO o PP)
        sub = sub[sub["fuente_financiacion"] == str(fuente).upper()]

    if estrato_grupo and "estrato_rango" in sub.columns:
        sub = sub[sub["estrato_rango"] == estrato_grupo]

    if sub.empty:
        return 0
    return int(sub["numero_usuarios_comuna"].fillna(0).sum())


def get_comunas_formateadas(df: pd.DataFrame) -> Tuple[List[str], Dict[str, str]]:
    """Retorna las opciones de selectbox y mapeo opción→nombre real."""
    if "Comuna Base" not in df.columns and "Nombre Comuna" in df.columns:
        df = df.copy()
        df["Comuna Base"] = df["Nombre Comuna"].apply(
            lambda x: str(x).split(" - ")[1] if " - " in str(x) else str(x)
        )

    if "Comuna Base" not in df.columns:
        return [], {}

    comunas_disponibles = sorted(df["Comuna Base"].dropna().unique())

    opciones: List[str] = ["TODAS LAS COMUNAS"]
    opciones += [format_comuna_con_numero(c) for c in comunas_disponibles]

    opcion_a_nombre: Dict[str, str] = {"TODAS LAS COMUNAS": "TODAS LAS COMUNAS"}
    for comuna in comunas_disponibles:
        opcion_a_nombre[format_comuna_con_numero(comuna)] = comuna

    return opciones, opcion_a_nombre
