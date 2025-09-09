from fastapi import APIRouter, HTTPException, Path, Body
from pydantic import BaseModel
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

# Modelo de entrada
class AssignLeadInput(BaseModel):
    assignedTo: UUID

# Endpoint para asignar o reasignar un lead
@router.put("/api/leads/{id}/assign")
def assign_lead(
    id: UUID = Path(..., description="ID del lead a asignar"),
    payload: AssignLeadInput = Body(...)
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar que el lead exista
        cursor.execute("""
            SELECT Id FROM dalilm.Leads WHERE Id = ?
        """, str(id))
        lead = cursor.fetchone()

        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")

        # Verificar que el usuario asignado exista y esté activo
        cursor.execute("""
            SELECT Id FROM dalilm.Users WHERE Id = ? AND IsActive = 1
        """, str(payload.assignedTo))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=404, detail="El usuario asignado no existe o no está activo")

        # Actualizar la asignación del lead
        cursor.execute("""
            UPDATE dalilm.Leads
            SET AssignedTo = ?, UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """, str(payload.assignedTo), str(id))

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "message": "Lead asignado correctamente.",
            "leadId": str(id),
            "assignedTo": str(payload.assignedTo)
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al asignar lead: {str(e)}")
