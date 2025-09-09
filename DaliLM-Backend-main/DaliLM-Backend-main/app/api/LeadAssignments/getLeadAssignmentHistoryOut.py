from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
import pyodbc
import os
from typing import List
from dotenv import load_dotenv


class LeadAssignmentHistoryOut(BaseModel):
    id: str
    lead_id: str
    from_user_id: Optional[str]
    from_user_name: Optional[str]
    to_user_id: str
    to_user_name: str
    assigned_by: str
    assigned_by_name: str
    assignment_reason: str
    previous_stage: Optional[str]
    current_stage: Optional[str]
    notes: Optional[str]
    assigned_at: str  # lo transformamos a isoformat()
    is_active: bool

router = APIRouter()
load_dotenv()

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('SQL_SERVER')};"
    f"DATABASE={os.getenv('SQL_DATABASE')};"
    f"UID={os.getenv('SQL_USERNAME')};"
    f"PWD={os.getenv('SQL_PASSWORD')}"
)

@router.get("/api/lead-assignments/user/{user_id}/history", response_model=List[LeadAssignmentHistoryOut])
def get_assignment_history_by_user(user_id: str):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    lah.Id,
                    lah.LeadId,
                    lah.FromUserId,
                    uf.Name AS FromUserName,
                    lah.ToUserId,
                    ut.Name AS ToUserName,
                    lah.AssignedBy,
                    ua.Name AS AssignedByName,
                    lah.AssignmentReason,
                    lah.PreviousStage,
                    lah.CurrentStage,
                    lah.Notes,
                    lah.AssignedAt,
                    lah.IsActive
                FROM dalilm.LeadAssignmentHistory lah
                LEFT JOIN dalilm.Users uf ON lah.FromUserId = uf.Id
                LEFT JOIN dalilm.Users ut ON lah.ToUserId = ut.Id
                LEFT JOIN dalilm.Users ua ON lah.AssignedBy = ua.Id
                WHERE lah.ToUserId = ? OR lah.AssignedBy = ?
                ORDER BY lah.AssignedAt DESC
            """
            cursor.execute(query, user_id, user_id)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = []
            for row in rows:
                record = dict(zip(columns, row))
                if isinstance(record["AssignedAt"], datetime):
                    record["AssignedAt"] = record["AssignedAt"].isoformat()
                results.append({
                    "id": record["Id"],
                    "lead_id": record["LeadId"],
                    "from_user_id": record["FromUserId"],
                    "from_user_name": record["FromUserName"],
                    "to_user_id": record["ToUserId"],
                    "to_user_name": record["ToUserName"],
                    "assigned_by": record["AssignedBy"],
                    "assigned_by_name": record["AssignedByName"],
                    "assignment_reason": record["AssignmentReason"],
                    "previous_stage": record["PreviousStage"],
                    "current_stage": record["CurrentStage"],
                    "notes": record["Notes"],
                    "assigned_at": record["AssignedAt"],
                    "is_active": record["IsActive"]
                })
            return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
