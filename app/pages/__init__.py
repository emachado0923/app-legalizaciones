# app/pages/__init__.py
from .overview import render_overview_page
from .citas import render_citas_page    # Nueva página

__all__ = [
    'render_overview_page',
    'render_citas_page'
]