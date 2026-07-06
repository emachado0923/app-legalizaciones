"""Páginas del dashboard Sapiencia."""

from app.pages.citas import render_citas_page
from app.pages.recurso_comunas import render_recurso_comunas_page

__all__ = [
    "render_citas_page",
    "render_recurso_comunas_page",
]
