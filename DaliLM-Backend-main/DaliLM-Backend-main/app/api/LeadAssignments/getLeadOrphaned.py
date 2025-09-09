from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv
from typing import List, Optional

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

class LeadOut(BaseModel):
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    document_number: Optional[int]
    company: Optional[str]
    source: str
    campaign: Optional[str]
    stage: str
    priority: str
    value: float
    assigned_to: Optional[str]
    created_at: str
    updated_at: str

@router.get("/api/lead-assignments/orphaned", response_model=List[LeadOut])
def get_orphaned_leads():
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM dalilm.Leads WHERE AssignedTo IS NULL and Stage <> 'Eliminado'"
            cursor.execute(query)

            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = []
            for row in rows:
                record = dict(zip(columns, row))
                record["CreatedAt"] = record["CreatedAt"].isoformat() if record["CreatedAt"] else None
                record["UpdatedAt"] = record["UpdatedAt"].isoformat() if record["UpdatedAt"] else None
                results.append({
                    "id": record["Id"],
                    "name": record["Name"],
                    "email": record["Email"],
                    "phone": record["Phone"],
                    "document_number": record["DocumentNumber"],
                    "company": record["Company"],
                    "source": record["Source"],
                    "campaign": record["Campaign"],
                    "stage": record["Stage"],
                    "priority": record["Priority"],
                    "value": float(record["Value"]),
                    "assigned_to": None,
                    "created_at": record["CreatedAt"],
                    "updated_at": record["UpdatedAt"]
                })

            return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
