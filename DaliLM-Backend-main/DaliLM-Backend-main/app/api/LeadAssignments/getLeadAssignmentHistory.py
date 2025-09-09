from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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

# Modelo de salida
class AssignmentRecord(BaseModel):
    id: UUID
    lead_id: UUID
    from_user_id: UUID | None
    from_user_name: str | None
    to_user_id: UUID
    to_user_name: str
    assigned_by: UUID
    assigned_by_name: str
    assignment_reason: str
    previous_stage: str | None
    current_stage: str | None
    notes: str | None
    assigned_at: str
    is_active: bool

# GET /api/lead-assignments/lead/{leadId}/history
@router.get("/api/lead-assignments/lead/{leadId}/history", response_model=list[AssignmentRecord])
def get_lead_assignment_history(leadId: UUID):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                lah.Id,
                lah.LeadId as lead_id,
                lah.FromUserId as from_user_id,
                fu.Name AS from_user_name,
                lah.ToUserId as to_user_id,
                tu.Name AS to_user_name,
                lah.AssignedBy as assigned_by,
                ab.Name AS assigned_by_name,
                lah.AssignmentReason as assignment_reason,
                lah.PreviousStage as previous_stage,
                lah.CurrentStage as current_stage,
                lah.Notes as notes,
                lah.AssignedAt as assigned_at,
                lah.IsActive as is_active
            FROM dalilm.LeadAssignmentHistory lah
            LEFT JOIN dalilm.Users fu ON lah.FromUserId = fu.Id
            LEFT JOIN dalilm.Users tu ON lah.ToUserId = tu.Id
            LEFT JOIN dalilm.Users ab ON lah.AssignedBy = ab.Id
            WHERE lah.LeadId = ?
            ORDER BY lah.AssignedAt DESC
        """, str(leadId))

        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        results = []
        for row in rows:
            record = dict(zip(columns, row))
            results.append({
                "id": record["Id"],
                "lead_id": record["lead_id"],
                "from_user_id": record["from_user_id"],
                "from_user_name": record["from_user_name"],
                "to_user_id": record["to_user_id"],
                "to_user_name": record["to_user_name"],
                "assigned_by": record["assigned_by"],
                "assigned_by_name": record["assigned_by_name"],
                "assignment_reason": record["assignment_reason"],
                "previous_stage": record["previous_stage"],
                "current_stage": record["current_stage"],
                "notes": record["notes"],
                "assigned_at": record["assigned_at"].isoformat() if record["assigned_at"] else None,
                "is_active": record["is_active"]
            })


        cursor.close()
        conn.close()

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar historial de asignaciones: {str(e)}")
