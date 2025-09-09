from fastapi import APIRouter, HTTPException, Query
import pyodbc
import os
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# Cargar .env
load_dotenv()

router = APIRouter()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

# Modelo
class Interaction(BaseModel):
    Id: UUID
    LeadId: UUID
    Type: str
    Description: str
    UserId: UUID
    Outcome: Optional[str] = None
    Stage: Optional[str] = None
    CreatedAt: datetime

@router.get("/api/interactions/recent", response_model=List[Interaction])
def get_recent_interactions(LeadId: Optional[UUID] = Query(None, description="Opcional: filtra por LeadId")):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        if LeadId:
            query = """
                SELECT TOP 20 Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt
                FROM dalilm.Interactions
                WHERE LeadId = ?
                ORDER BY CreatedAt DESC
            """
            cursor.execute(query, str(LeadId))
        else:
            query = """
                SELECT TOP 50 Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt
                FROM dalilm.Interactions
                ORDER BY CreatedAt DESC
            """
            cursor.execute(query)

        rows = cursor.fetchall()
        results = [
            Interaction(
                Id=row.Id,
                LeadId=row.LeadId,
                Type=row.Type,
                Description=row.Description,
                UserId=row.UserId,
                Outcome=row.Outcome,
                Stage=row.Stage,
                CreatedAt=row.CreatedAt.isoformat()
            )
            for row in rows
        ]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener interacciones recientes: {str(e)}")
    finally:
        cursor.close()
        conn.close()
