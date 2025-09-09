from fastapi import APIRouter, HTTPException, Query
import pyodbc
import os
from pydantic import BaseModel, EmailStr, field_validator
from dotenv import load_dotenv
import json

from uuid import uuid4

# Carga del .env solo para desarrollo local
load_dotenv()

# Configuración de la base de datos
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

# Crear router de FastAPI
router = APIRouter()

@router.get("/api/users/search")
def search_users(
    query: str = Query(..., description="Texto a buscar en nombre o email")
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        sql_query = """
            SELECT *
            FROM dalilm.Users
            WHERE Name LIKE ? OR Email LIKE ?
            ORDER BY CreatedAt DESC
        """
        search_param = f"%{query}%"
        cursor.execute(sql_query, search_param, search_param)

        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al buscar usuarios: {str(e)}")
