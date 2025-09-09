from fastapi import APIRouter, HTTPException, Query
import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

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

@router.get("/api/users/list")
def get_users(
    name: str = Query(None, description="Filtrar por nombre"),
    email: str = Query(None, description="Filtrar por email"),
    role: str = Query(None, description="Filtrar por rol"),
    is_active: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a devolver"),
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Construir la consulta dinámica
        query = "SELECT * FROM dalilm.Users"
        params = []

        if name:
            query += " AND Name LIKE ?"
            params.append(f"%{name}%")
        if email:
            query += " AND Email LIKE ?"
            params.append(f"%{email}%")
        if role:
            query += " AND Role = ?"
            params.append(role)
        if is_active is not None:
            query += " AND IsActive = ?"
            params.append(1 if is_active else 0)

        query += " ORDER BY CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([skip, limit])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {str(e)}")
