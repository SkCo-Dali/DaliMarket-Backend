from fastapi import APIRouter, HTTPException, Path
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv
from typing import List
from pydantic import BaseModel
from datetime import datetime

# Cargar .env
load_dotenv()

router = APIRouter()

# Configuración de conexión
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)

# Modelo de respuesta
class Interaction(BaseModel):
    Id: UUID
    LeadId: UUID
    Type: str
    Description: str
    UserId: UUID
    Outcome: str = None
    Stage: str = None
    CreatedAt: datetime

@router.get("/api/interactions/user/{userId}", response_model=List[Interaction])
def get_interactions_by_user(userId: UUID):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt
            FROM dalilm.Interactions
            WHERE UserId = ?
            ORDER BY CreatedAt DESC
        """, str(userId))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append(Interaction(
                Id=row.Id,
                LeadId=row.LeadId,
                Type=row.Type,
                Description=row.Description,
                UserId=row.UserId,
                Outcome=row.Outcome,
                Stage=row.Stage,
                CreatedAt=row.CreatedAt.isoformat()
            ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener interacciones: {str(e)}")
    finally:
        cursor.close()
        conn.close()
