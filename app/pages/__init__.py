"""Páginas del dashboard Sapiencia."""

from app.pages.citas import render_citas_page
from app.pages.estadisticas_legalizacion import render_estadisticas_legalizacion
from app.pages.recurso_comunas import render_recurso_comunas_page

__all__ = [
    "render_citas_page",
    "render_estadisticas_legalizacion",
    "render_recurso_comunas_page",
]
