# infrastructure/adapters/sql_server_adapter.py
import logging
import pyodbc
from core.settings import settings
from core.exceptions import ConnectionErrorException

class SqlServerAdapter:
    def __init__(self):
        self.connection_string = (
            f"DRIVER={settings.SQL_DRIVER};"
            f"SERVER={settings.SQL_SERVER};"
            f"DATABASE={settings.SQL_DATABASE};"
            f"UID={settings.SQL_USERNAME};"
            f"PWD={settings.SQL_PASSWORD};"
        )

    def get_connection(self):
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            logging.error(f"Error al conectar con SQL Server: {str(e)}")
            raise ConnectionErrorException("No se pudo establecer conexión con SQL Server.")

    def execute_query(self, query: str, params: tuple = None, fetchone=False, fetchall=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None

            conn.commit()
            return result
        finally:
            cursor.close()
            conn.close()

def get_sql_server_session():
    return SqlServerAdapter()
