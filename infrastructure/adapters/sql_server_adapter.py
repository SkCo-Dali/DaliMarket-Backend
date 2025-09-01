# infrastructure/adapters/sql_server.py
import logging
import pyodbc
from core.settings import settings
from core.exceptions import ConnectionErrorException


class SqlServerAdapter:
    def __init__(self):
        try:
            driver = "{ODBC Driver 17 for SQL Server}"
            self.connection_string = (
                f"DRIVER={driver};"
                f"SERVER={settings.SQL_SERVER};"
                f"DATABASE={settings.SQL_DATABASE};"
                f"UID={settings.SQL_USERNAME};"
                f"PWD={settings.SQL_PASSWORD};"
            )
            self.conn = pyodbc.connect(self.connection_string)
        except Exception as e:
            logging.error(f"Error al conectar con SQL Server: {str(e)}")
            raise ConnectionErrorException("No se pudo establecer conexión con SQL Server.")

    def get_cursor(self):
        return self.conn.cursor()

    def execute_query(self, query: str, params: tuple = None, fetchone=False, fetchall=False):
        """
        Ejecuta un query en la base de datos SQL Server.
        """
        cursor = self.get_cursor()
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

            self.conn.commit()
            return result
        finally:
            cursor.close()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None


def get_sql_server_session():
    db = SqlServerAdapter()
    try:
        yield db
    finally:
        db.close()
