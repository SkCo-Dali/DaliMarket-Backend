from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

# Conexión SQL Server
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
class LeadReassignmentRequest(BaseModel):
    lead_id: UUID = Field(..., description="ID del Lead a reasignar")
    from_user_id: UUID = Field(..., description="ID del usuario actual")
    to_user_id: UUID = Field(..., description="ID del nuevo usuario")
    assigned_by: UUID = Field(..., description="ID del usuario que reasigna (quien hace la acción)")
    reason: str = Field(..., max_length=100, description="Motivo de la reasignación")
    notes: str | None = Field(None, description="Notas adicionales")

# Endpoint POST /api/lead-assignments/reassign
@router.post("/api/lead-assignments/reassign")
def reassign_lead(payload: LeadReassignmentRequest):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            EXEC dalilm.sp_ReassignLead
                @LeadId = ?,
                @FromUserId = ?,
                @ToUserId = ?,
                @AssignedBy = ?,
                @Reason = ?,
                @Notes = ?
        """, (
            str(payload.lead_id),
            str(payload.from_user_id),
            str(payload.to_user_id),
            str(payload.assigned_by),
            payload.reason,
            payload.notes
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Reasignación exitosa"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reasignar lead: {str(e)}")
