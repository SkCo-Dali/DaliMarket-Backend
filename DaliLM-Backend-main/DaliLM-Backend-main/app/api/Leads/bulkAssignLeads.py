from fastapi import APIRouter, HTTPException
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

# ✔️ Modelo del body
class BulkAssignRequest(BaseModel):
    leadIds: list[UUID]
    assignedTo: UUID

    @field_validator("leadIds")
    def check_lead_list_not_empty(cls, v):
        if not v:
            raise ValueError("La lista de leads no puede estar vacía.")
        return v


@router.post("/api/leads/bulk-assign")
def bulk_assign_leads(payload: BulkAssignRequest):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # ✔️ Verificar si el usuario asignado existe
        cursor.execute("SELECT 1 FROM dalilm.Users WHERE Id = ?", str(payload.assignedTo))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario asignado no encontrado")

        # ✔️ Validar leads uno a uno
        missing_leads = []
        for lead_id in payload.leadIds:
            cursor.execute("SELECT 1 FROM dalilm.Leads WHERE Id = ?", str(lead_id))
            if not cursor.fetchone():
                missing_leads.append(str(lead_id))

        if missing_leads:
            raise HTTPException(
                status_code=404,
                detail=f"Los siguientes leads no existen: {', '.join(missing_leads)}"
            )

        # ✔️ Realizar la asignación masiva
        for lead_id in payload.leadIds:
            cursor.execute("""
                UPDATE dalilm.Leads
                SET AssignedTo = ?, UpdatedAt = GETUTCDATE(), Stage = 'Asignado'
                WHERE Id = ?
            """, str(payload.assignedTo), str(lead_id))

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "message": f"Leads asignados exitosamente al usuario {payload.assignedTo}.",
            "assignedLeads": [str(lead_id) for lead_id in payload.leadIds]
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al asignar leads: {str(e)}")
