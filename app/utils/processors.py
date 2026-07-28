"""Procesamiento y cálculo de métricas sobre DataFrames de presupuesto."""
from __future__ import annotations

from typing import Any, Dict, Optional

import pandas as pd

from app.config import COMUNA_MAPPING


# ---------------------------------------------------------------------------
# Derivación de `fuente_financiacion` desde el código de `comuna`.
#
# La tabla `callg_control_presupuesto_comuna_fidu` NO contiene una columna
# explícita con el fondo: la fuente de financiación se infiere del valor de
# `comuna` siguiendo los identificadores definidos en
# `CONFIGURACION_ESTRATOS_FONDOS`. Esta función centraliza ese mapeo.
# ---------------------------------------------------------------------------
def _derivar_fondo(comuna: Any) -> Optional[str]:
    """Devuelve el nombre del fondo (`fuente_financiacion`) según `comuna`.

    Reglas, en orden:
    1. Códigos que empiezan con `220456` y son más largos → EXTENDIENDO
       FRONTERAS - PRESUPUESTO PARTICIPATIVO (uno por comuna/corregimiento).
    2. Códigos ENLAZA MUNDOS: `2214561..2214564` = RO por modalidad;
       `221456X + id_comuna` = PP por (modalidad, comuna).  [V6.12]
    3. Códigos puntuales (`220456`, `219456`, `100234`, `100235`).
    4. Sufijo `123` o `456` con código corto → PRESUPUESTO PARTICIPATIVO
       (pregrado).
    """
    if comuna is None or pd.isna(comuna):
        return None
    comuna_str = str(comuna).strip()
    if not comuna_str:
        return None

    # 1. EXTENDIENDO FRONTERAS - PP (códigos 2204561 .. 22045690)
    if comuna_str.startswith("220456") and len(comuna_str) > 6:
        return "EXTENDIENDO FRONTERAS - PRESUPUESTO PARTICIPATIVO"

    # V6.12: ENLAZA MUNDOS
    # - 7 dígitos exactos (2214561..2214564) → RO por modalidad
    # - 7+ dígitos (`221456X` + id_comuna) → PP
    if comuna_str.startswith("221456") and len(comuna_str) >= 7:
        if len(comuna_str) == 7:
            return "ENLAZA MUNDOS - RECURSO ORDINARIO"
        return "ENLAZA MUNDOS - PRESUPUESTO PARTICIPATIVO"

    # 2. Códigos puntuales
    codigos_puntuales = {
        "220456": "EXTENDIENDO FRONTERAS - RECURSO ORDINARIO",
        "219456": "FORMACION AVANZADA",
        "100234": "RECURSO ORDINARIO",
        # SUPUESTO: el código 100235 no aparece en el spec original; la
        # escala de usuarios (6 vs 247) sugiere que corresponde al fondo
        # de MEJORES DEPORTISTAS. Si se confirma otro fondo, ajustar aquí.
        "100235": "MEJORES DEPORTISTAS",
        # V7: CDJ (Consejeros Distritales de Juventudes)
        "100237": "CONSEJEROS DISTRITALES DE JUVENTUDES",
    }
    if comuna_str in codigos_puntuales:
        return codigos_puntuales[comuna_str]

    # 3. Pregrado: PRESUPUESTO PARTICIPATIVO por sufijo 123/456
    if comuna_str.endswith("123") or comuna_str.endswith("456"):
        return "PRESUPUESTO PARTICIPATIVO"

    return None


def _derivar_estrato_rango(comuna: Any) -> Optional[str]:
    """Etiqueta del rango de estratos representado por la fila.

    Útil para filtrar tarjetas dinámicas:
    - sufijo `123` → "1-3"
    - sufijo `456` → "4-6"
    - resto → None (la tarjeta se renderiza con todas las filas del fondo)
    """
    if comuna is None or pd.isna(comuna):
        return None
    comuna_str = str(comuna).strip()
    # EXTENDIENDO FRONTERAS - PP: el sufijo 456 forma parte del prefijo, no
    # del estrato; descartar antes de buscar sufijo de estrato.
    if comuna_str.startswith("220456") and len(comuna_str) > 6:
        return None
    # V6.12: ENLAZA MUNDOS — todos los códigos son 1-6, sin sufijo de estrato
    if comuna_str.startswith("221456"):
        return None
    if comuna_str.endswith("123"):
        return "1-3"
    if comuna_str.endswith("456") and comuna_str not in {"219456", "220456"}:
        return "4-6"
    return None


def process_comuna_data(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece el DataFrame de presupuesto con columnas derivadas.

    - Convierte columnas numéricas a int (NaN → 0).
    - Detecta sufijo 123/456 en `comuna` para clasificar estrato (legacy).
    - Mapea `comuna` a `Nombre Comuna` usando `COMUNA_MAPPING`.
    - Extrae `Comuna Base` a partir del nombre formateado.
    """
    if df.empty:
        return df

    df = df.copy()

    numeric_columns = [
        "presupuesto_comuna",
        "restante_presupuesto_comuna",
        "acumulado_legali_comuna",
        "numero_usuarios_comuna",
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        else:
            df[col] = 0

    if "comuna" in df.columns:
        df["comuna_str"] = df["comuna"].astype(str)

        # Derivar fondo y rango de estrato a partir del código de comuna
        # (la tabla no expone una columna `fuente_financiacion` directa).
        df["fuente_financiacion"] = df["comuna"].apply(_derivar_fondo)
        df["estrato_rango"] = df["comuna"].apply(_derivar_estrato_rango)

        # Clasificación legacy 1-3 / 4-6 para la tabla resumen general.
        df["es_123"] = df["estrato_rango"] == "1-3"
        df["grupo_estrato"] = df["estrato_rango"].apply(
            lambda x: f"Estratos {x}" if x else "Sin estrato definido"
        )

        df["Nombre Comuna"] = df["comuna_str"].map(COMUNA_MAPPING)
        df["Nombre Comuna"] = df["Nombre Comuna"].fillna(
            "Comuna " + df["comuna_str"].astype(str)
        )

        df["Comuna Base"] = df["Nombre Comuna"].apply(
            lambda x: x.split(" - ")[1] if " - " in str(x) else str(x)
        )

    return df


def calculate_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula totales agregados para mostrar en métricas superiores."""
    if df.empty:
        return {
            "total_presupuesto": 0,
            "total_consumido": 0,
            "total_restante": 0,
            "total_usuarios": 0,
            "total_comunas": 0,
            "porcentaje_utilizacion": 0.0,
        }

    total_presupuesto = int(df.get("presupuesto_comuna", pd.Series(dtype=int)).sum())
    total_restante = int(df.get("restante_presupuesto_comuna", pd.Series(dtype=int)).sum())
    total_consumido = total_presupuesto - total_restante
    total_usuarios = int(df.get("numero_usuarios_comuna", pd.Series(dtype=int)).sum())
    total_comunas = (
        df["Nombre Comuna"].nunique() if "Nombre Comuna" in df.columns else 0
    )

    porcentaje = (
        (total_consumido / total_presupuesto * 100) if total_presupuesto > 0 else 0.0
    )

    return {
        "total_presupuesto": total_presupuesto,
        "total_consumido": total_consumido,
        "total_restante": total_restante,
        "total_usuarios": total_usuarios,
        "total_comunas": total_comunas,
        "porcentaje_utilizacion": porcentaje,
    }
