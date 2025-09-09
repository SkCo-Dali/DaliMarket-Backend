from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import List

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


@router.get("/api/lead-assignments/user/{user_id}/current", response_model=List[dict])
def get_current_leads_for_user(user_id: UUID):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = """
        SELECT 
            l.Id AS LeadId,
            l.Name AS LeadName,
            l.Email,
            l.Phone,
            l.Stage,
            l.Priority,
            l.Value,
            l.Source,
            l.Campaign,
            l.CreatedAt,
            lah.AssignedAt
        FROM dalilm.LeadAssignmentHistory lah
        INNER JOIN dalilm.Leads l 
        ON lah.LeadId = l.Id
        WHERE lah.ToUserId = ? AND lah.IsActive = 1
        ORDER BY lah.AssignedAt DESC
        """
        cursor.execute(query, str(user_id))
        columns = [column[0] for column in cursor.description]
        results = [
            dict(zip(columns, row)) for row in cursor.fetchall()
        ]

        # Convertir fechas a string ISO para evitar errores
        for r in results:
            if isinstance(r["CreatedAt"], datetime):
                r["CreatedAt"] = r["CreatedAt"].isoformat()
            if isinstance(r["AssignedAt"], datetime):
                r["AssignedAt"] = r["AssignedAt"].isoformat()

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
