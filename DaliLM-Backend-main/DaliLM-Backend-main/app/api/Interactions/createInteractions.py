from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime
import pyodbc
import os
from dotenv import load_dotenv
import json

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

# ----------- Modelo Pydantic -----------
class InteractionInput(BaseModel):
    LeadId: UUID
    UserId: UUID
    Type: str = Field(..., pattern="^(note|whatsapp|meeting|email|call)$")
    Description: str
    Stage: str = Field(..., max_length=50)
    Outcome: Optional[str] = Field(None, pattern="^(positive|neutral|negative)?$")


# --------- Endpoint para crear interacción ---------
@router.post("/api/interactions")
def create_interaction(payload: InteractionInput = Body(...)):
    try:
        interaction_id = str(uuid4())

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Validar que el Lead exista
        cursor.execute("SELECT 1 FROM dalilm.Leads WHERE Id = ?", str(payload.LeadId))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="El Lead especificado no existe.")

        # Validar que el usuario exista
        cursor.execute("SELECT 1 FROM dalilm.Users WHERE Id = ?", str(payload.UserId))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="El Usuario especificado no existe.")

        # Insertar la interacción
        cursor.execute("""
            INSERT INTO dalilm.Interactions (
                Id, LeadId, Type, Description, UserId, Outcome, Stage, CreatedAt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, GETUTCDATE())
        """, interaction_id, str(payload.LeadId), payload.Type, payload.Description,
              str(payload.UserId), payload.Outcome, payload.Stage)

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "message": "Interacción registrada exitosamente",
            "interaction": {
                "Id": interaction_id,
                "LeadId": str(payload.LeadId),
                "Type": payload.Type,
                "Description": payload.Description,
                "UserId": str(payload.UserId),
                "Outcome": payload.Outcome,
                "Stage": payload.Stage
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar interacción: {str(e)}")
