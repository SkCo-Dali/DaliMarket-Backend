from pydantic import BaseModel, EmailStr, field_validator
from fastapi import APIRouter, HTTPException, Path
from uuid import UUID
import pyodbc
import os
import json
from dotenv import load_dotenv

# Cargar .env
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

@router.delete("/api/leads/{id}")
def delete_lead(
    id: UUID = Path(..., description="ID del lead en formato UUID")
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar que el lead exista
        cursor.execute("""
            SELECT 1 FROM dalilm.Leads WHERE Id = ?
        """, str(id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        # Soft delete → marcar como etapa 'Eliminado'
        cursor.execute("""
            UPDATE dalilm.Leads
            SET Stage = 'Eliminado', UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """, str(id))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Lead eliminado correctamente (soft delete)."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar lead: {str(e)}")
