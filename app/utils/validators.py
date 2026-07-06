"""Validadores y búsquedas sobre datos del usuario."""
from __future__ import annotations

from typing import Any

import pandas as pd

# CORRECCIÓN V4: una sola implementación de normalización en formatters.
from app.utils.formatters import formatear_documento as _normalizar_documento


def es_documento_valido(documento: Any) -> bool:
    """Valida que el input contenga solo dígitos (sin puntos ni espacios)."""
    if documento is None:
        return False
    documento_limpio = str(documento).strip()
    return documento_limpio.isdigit() and len(documento_limpio) > 0


def buscar_por_documento(df: pd.DataFrame, valor_busqueda: str) -> pd.DataFrame:
    """Busca un beneficiario por número de documento.

    Lógica:
        1. Primero busca coincidencia exacta en la columna `documento`.
        2. Si no encuentra resultados, o todos los valores de esa columna
           están vacíos/NaN, hace fallback a `hist_documento`.

    Args:
        df: DataFrame con columnas `documento` y `hist_documento` (al menos
            una de ellas debe existir).
        valor_busqueda: cadena con el número de documento a buscar.

    Returns:
        Subconjunto del DataFrame con los registros encontrados. DataFrame
        vacío si no hay coincidencias o el valor de búsqueda está vacío.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    valor = (valor_busqueda or "").strip()
    if not valor:
        return pd.DataFrame()

    valor_normalizado = _normalizar_documento(valor)
    if not valor_normalizado:
        return pd.DataFrame()

    resultado = pd.DataFrame()

    # Búsqueda primaria en 'documento' (normalizando ambos lados)
    if "documento" in df.columns:
        documento_norm = df["documento"].map(_normalizar_documento)
        resultado = df[documento_norm == valor_normalizado]

    # Fallback a 'hist_documento' si:
    #   - no hubo resultados, o
    #   - los registros encontrados tienen 'documento' nulo/vacío
    necesita_fallback = (
        resultado.empty
        or (
            "documento" in df.columns
            and df.loc[resultado.index, "documento"].isna().all()
        )
    )
    if necesita_fallback and "hist_documento" in df.columns:
        hist_norm = df["hist_documento"].map(_normalizar_documento)
        resultado = df[hist_norm == valor_normalizado]

    return resultado
