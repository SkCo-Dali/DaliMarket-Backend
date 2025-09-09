from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

# Configuración conexión SQL
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
class InteractionOut(BaseModel):
    Id: str
    LeadId: str
    Type: str
    Description: str
    UserId: str
    Outcome: Optional[str] = None
    Stage: Optional[str] = None
    CreatedAt: datetime

# API: Obtener interacciones de un lead
@router.get("/api/interactions/lead/{leadId}", response_model=List[InteractionOut])
def get_interactions_by_lead(leadId: str):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = """
            SELECT Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt
            FROM dalilm.Interactions
            WHERE LeadId = ?
            
        """
        cursor.execute(query, (leadId,))
        rows = cursor.fetchall()

        interactions = []
        columns = [column[0] for column in cursor.description]
        for row in rows:
            interactions.append(dict(zip(columns, row)))

        cursor.close()
        conn.close()

        return interactions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener interacciones: {str(e)}")
