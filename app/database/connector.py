"""Conector MySQL con manejo seguro de conexiones y caché.

Reglas importantes:
- Las **conexiones NO se cachean** (solo los DataFrames resultantes).
- Toda función pública usa context manager para cerrar en bloque `finally`.
- Errores se propagan como `DatabaseError` y se traducen a `st.error()` en
  la capa de presentación (no aquí).
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator, List, Optional, Sequence

import mysql.connector
import pandas as pd
from mysql.connector import Error as MySQLError

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseError(RuntimeError):
    """Error genérico de la capa de base de datos."""


def _build_connection_kwargs() -> dict[str, Any]:
    """Construye los kwargs para `mysql.connector.connect`.

    Los valores vienen de `settings`, que siempre tiene defaults para
    todas las variables de BD; por eso NO se hace validación de presencia.
    """
    return {
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "database": settings.DB_NAME,
        "user": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "connection_timeout": 10,
    }


@contextmanager
def get_connection() -> Iterator[mysql.connector.MySQLConnection]:
    """Context manager que abre una conexión MySQL y la cierra siempre.

    Uso:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            ...
    """
    connection: Optional[mysql.connector.MySQLConnection] = None
    try:
        connection = mysql.connector.connect(**_build_connection_kwargs())
        yield connection
    except MySQLError as exc:
        logger.exception("Error MySQL al abrir conexión")
        raise DatabaseError(f"No se pudo conectar a MySQL: {exc}") from exc
    finally:
        if connection is not None and connection.is_connected():
            try:
                connection.close()
            except MySQLError:
                logger.warning("Error al cerrar conexión MySQL", exc_info=True)


def fetch_query(query: str, params: Sequence[Any] | None = None) -> List[dict[str, Any]]:
    """Ejecuta un SELECT y retorna la lista de filas como diccionarios.

    Args:
        query: SQL parametrizado con `%s`.
        params: secuencia de valores para los placeholders (o None).
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                return cursor.fetchall()
            finally:
                cursor.close()
    except MySQLError as exc:
        logger.exception("Error ejecutando consulta")
        raise DatabaseError(f"Error ejecutando consulta: {exc}") from exc


# ---------------------------------------------------------------------------
# Consultas de dominio (devuelven DataFrames listos para usar)
# ---------------------------------------------------------------------------
def fetch_presupuesto_comuna(periodo: int | None = None) -> pd.DataFrame:
    """Trae la tabla de presupuesto por comuna para un periodo dado."""
    periodo_real = periodo if periodo is not None else settings.CURRENT_PERIOD
    query = f"SELECT * FROM {settings.TABLE_PRESUPUESTO} WHERE periodo = %s"
    rows = fetch_query(query, (periodo_real,))
    return pd.DataFrame(rows)


def fetch_citas() -> pd.DataFrame:
    """Trae el histórico completo de citas desde la vista nueva.

    Vista: convocatoria_sapiencia.vw_callg_control_citas_con_historico
    Columnas esperadas: taquilla, fecha, hora_inicio, nombre, documento,
    linea, estado, id_usuario, hist_id, hist_id_usuario, hist_nombre,
    hist_documento, hist_observacion, hist_fecha_registro.
    """
    query = f"""
        SELECT *
        FROM {settings.VISTA_CITAS}
        ORDER BY fecha DESC, hora_inicio DESC, hist_fecha_registro DESC
    """
    rows = fetch_query(query)
    return pd.DataFrame(rows)


# V5.10: nueva página Estadísticas Legalización
def fetch_giros_informe(convocatoria: str = "2026-2") -> pd.DataFrame:
    """Trae los registros de la vista `vw_giros_informe_total` filtrados por convocatoria.

    Columnas clave usadas por la página:
        fondo, Tipo_solicitud_definitiva, Comuna_de_residencia, Estrato,
        Valor_matricula, Valor_sostenimiento, Pagare, IES, Programa_academico.
    """
    query = "SELECT * FROM vw_giros_informe_total WHERE Convocatoria = %s"
    rows = fetch_query(query, (convocatoria,))
    return pd.DataFrame(rows)
