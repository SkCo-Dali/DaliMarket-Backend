from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, field_validator
from uuid import UUID
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

# Modelo del body
class StageUpdateRequest(BaseModel):
    stage: str



@router.put("/api/leads/{id}/stage")
def update_lead_stage(
    id: UUID = Path(..., description="ID del lead"),
    payload: StageUpdateRequest = Body(...)
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar que el lead exista
        cursor.execute("SELECT Id FROM dalilm.Leads WHERE Id = ?", str(id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Lead no encontrado")

        # Actualizar la etapa
        cursor.execute("""
            UPDATE dalilm.Leads
            SET Stage = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """, payload.stage, str(id))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "message": f"Etapa del lead {id} actualizada exitosamente a '{payload.stage}'."
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar la etapa del lead: {str(e)}")
