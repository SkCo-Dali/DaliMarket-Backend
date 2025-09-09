from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pyodbc
import os
from dotenv import load_dotenv
from uuid import UUID

# Cargar .env
load_dotenv()

router = APIRouter()

# Conexión SQL
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USERNAME = os.getenv("SQL_USERNAME")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};"
    f"UID={SQL_USERNAME};PWD={SQL_PASSWORD}"
)


class MergeLeadsRequest(BaseModel):
    leadIds: list[UUID]
    primaryLeadId: UUID


@router.post("/api/leads/merge")
def merge_leads(payload: MergeLeadsRequest):
    try:
        lead_ids = payload.leadIds
        primary_id = str(payload.primaryLeadId)

        if primary_id not in [str(lid) for lid in lead_ids]:
            raise HTTPException(status_code=400, detail="primaryLeadId debe estar dentro de leadIds")

        secondary_ids = [str(lid) for lid in lead_ids if str(lid) != primary_id]

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar que todos los leads existen
        cursor.execute(
            f"SELECT Id FROM dalilm.Leads WHERE Id IN ({','.join(['?'] * len(lead_ids))})",
            *lead_ids
        )
        rows = cursor.fetchall()

        if len(rows) != len(lead_ids):
            raise HTTPException(status_code=404, detail="Uno o más leads no existen.")

        # Migrar Interactions
        cursor.execute(
            f"""
            UPDATE dalilm.Interactions 
            SET LeadId = ? 
            WHERE LeadId IN ({','.join(['?'] * len(secondary_ids))})
            """,
            primary_id, *secondary_ids
        )

        # Migrar Tasks
        cursor.execute(
            f"""
            UPDATE dalilm.Tasks 
            SET LeadId = ? 
            WHERE LeadId IN ({','.join(['?'] * len(secondary_ids))})
            """,
            primary_id, *secondary_ids
        )

        # Eliminar Leads secundarios
        cursor.execute(
            f"""
            DELETE FROM dalilm.Leads 
            WHERE Id IN ({','.join(['?'] * len(secondary_ids))})
            """,
            *secondary_ids
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "message": "Leads fusionados correctamente",
            "primaryLeadId": primary_id,
            "removedLeadIds": secondary_ids
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al fusionar leads: {str(e)}")
