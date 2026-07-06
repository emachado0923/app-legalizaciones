"""Gráficos reutilizables con Plotly.

Placeholder con utilidades base para futuros gráficos (distribución por
fondo, evolución temporal, comparativos). Se mantiene un módulo separado
para crecer sin recargar `cards.py` / `tables.py`.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.config import SAPIENCIA_COLORS


def _paleta_sapiencia() -> list[str]:
    """Lista ordenada de colores para series de Plotly."""
    return [
        SAPIENCIA_COLORS["magenta_primary"],
        SAPIENCIA_COLORS["magenta_light"],
        SAPIENCIA_COLORS["magenta_dark"],
        SAPIENCIA_COLORS["success_green"],
        SAPIENCIA_COLORS["warning_amber"],
        SAPIENCIA_COLORS["error_red"],
        SAPIENCIA_COLORS["gray_medium"],
    ]


def aplicar_tema_sapiencia(fig: go.Figure) -> go.Figure:
    """Aplica colores y tipografía Sapiencia a una figura Plotly existente."""
    fig.update_layout(
        font_family="Calibri, Arial, sans-serif",
        font_color=SAPIENCIA_COLORS["gray_dark"],
        title_font_color=SAPIENCIA_COLORS["magenta_primary"],
        title_font_size=18,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=_paleta_sapiencia(),
    )
    return fig


def grafico_barra_presupuesto_por_comuna(df: pd.DataFrame, columna_valor: str = "presupuesto_comuna") -> go.Figure:
    """Barras horizontales de presupuesto por comuna (helper inicial)."""
    if df.empty or "Nombre Comuna" not in df.columns or columna_valor not in df.columns:
        return go.Figure()

    agg = (
        df.groupby("Nombre Comuna", as_index=False)[columna_valor]
        .sum()
        .sort_values(columna_valor, ascending=True)
    )

    fig = px.bar(
        agg,
        x=columna_valor,
        y="Nombre Comuna",
        orientation="h",
        title="Presupuesto por comuna",
    )
    return aplicar_tema_sapiencia(fig)
