from fastapi import APIRouter, HTTPException, Path
import pyodbc
import os
from dotenv import load_dotenv
from uuid import UUID

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

@router.get("/api/users/roles")
def get_user_roles():
    try:
        roles = ['admin', 'seguridad', 'analista', 'supervisor', 'gestor', 'director', 'promotor', 'aliado', 'socio', 'fp']
        return {"roles": roles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los roles: {str(e)}")
