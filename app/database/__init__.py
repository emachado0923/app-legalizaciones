"""Paquete de acceso a base de datos.

Reexporta las funciones principales:
- `get_connection()`: context manager para conexión MySQL
- `fetch_query()`: ejecuta SELECT y retorna lista de dicts
- `fetch_presupuesto_comuna()`: dataframe de presupuesto por comuna
- `fetch_citas()`: dataframe del histórico de citas
"""

from app.database.connector import (
    get_connection,
    fetch_query,
    fetch_presupuesto_comuna,
    fetch_citas,
    DatabaseError,
)

__all__ = [
    "get_connection",
    "fetch_query",
    "fetch_presupuesto_comuna",
    "fetch_citas",
    "DatabaseError",
]
