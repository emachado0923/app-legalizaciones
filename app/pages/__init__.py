# app/pages/__init__.py
from .overview import render_overview_page
from .detail import render_detail_page

__all__ = ['render_overview_page', 'render_detail_page']