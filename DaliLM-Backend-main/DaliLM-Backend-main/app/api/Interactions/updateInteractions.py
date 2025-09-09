from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
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

# Modelo para actualizar la interacción
class InteractionUpdate(BaseModel):
    Type: Optional[str] = Field(None, pattern="^(note|whatsapp|meeting|email|call)$")
    Description: Optional[str]
    UserId: Optional[UUID]
    Outcome: Optional[str] = Field(None, pattern="^(positive|neutral|negative)?$")
    Stage: Optional[str]

    @field_validator("Description")
    def validate_description(cls, v):
        if v is not None and not v.strip():
            raise ValueError("La descripción no puede estar vacía")
        return v

@router.put("/api/interactions/{id}")
def update_interaction(id: UUID, payload: InteractionUpdate):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar si la interacción existe
        cursor.execute("SELECT COUNT(*) FROM dalilm.Interactions WHERE Id = ?", str(id))
        if cursor.fetchone()[0] == 0:
            raise HTTPException(status_code=404, detail="Interacción no encontrada")

        # Construir SET dinámico
        updates = []
        values = []

        for field, value in payload.model_dump(exclude_unset=True).items():
            updates.append(f"{field} = ?")
            values.append(value)

        if not updates:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")

        query = f"""
            UPDATE dalilm.Interactions
            SET {', '.join(updates)}
            WHERE Id = ?
        """
        values.append(str(id))
        cursor.execute(query, values)
        conn.commit()

        return {"message": "Interacción actualizada correctamente"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar interacción: {str(e)}")
    finally:
        cursor.close()
        conn.close()