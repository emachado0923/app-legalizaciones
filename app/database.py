# app/database.py
import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
from app.config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
    
    def get_connection(self):
        """Crear y retornar una conexión a la base de datos"""
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                return connection
            return None
        except Error as e:
            st.error(f"❌ Error al conectar con MySQL: {e}")
            return None
    
    def execute_query(self, query, params=None):
        """Ejecutar una consulta y retornar resultados como diccionarios"""
        connection = self.get_connection()
        if connection is None:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Error as e:
            st.error(f"❌ Error al ejecutar consulta: {e}")
            if connection.is_connected():
                connection.close()
            return None
    
    def fetch_all_data(self, table_name, period=15):
        """Obtener todos los datos de una tabla para un periodo específico"""
        query = f"""
        SELECT * 
        FROM {table_name} 
        WHERE periodo = %s
        """
        return self.execute_query(query, (period,))

# Instancia global de la base de datos
db = DatabaseManager()