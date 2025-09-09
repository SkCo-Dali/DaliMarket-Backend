from fastapi import APIRouter, HTTPException, Path, Query
from uuid import UUID
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


@router.get("/api/leads/assigned-to/{userId}")
def get_leads_assigned_to_user(
    userId: UUID = Path(..., description="ID del usuario al que están asignados los leads"),
    stage: str | None = Query(None, description="Filtrar por etapa del lead (opcional)"),
    priority: str | None = Query(None, description="Filtrar por prioridad del lead (opcional)")
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar si el usuario existe
        cursor.execute("SELECT Id FROM dalilm.Users WHERE Id = ?", str(userId))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Construir la consulta dinámica con filtros opcionales
        query = """
            SELECT CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                   Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                   NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, 
                   Age, Gender, PreferredContactChannel, AdditionalInfo
            FROM dalilm.Leads
            WHERE (Stage IS NULL OR Stage <> 'Eliminado') and AssignedTo = ?
        """
        params = [str(userId)]

        if stage:
            query += " AND Stage = ?"
            params.append(stage)

        if priority:
            query += " AND Priority = ?"
            params.append(priority)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        leads = []

        for row in rows:
            lead = dict(zip(columns, row))

            # Convertir campos JSON almacenados como texto a listas
            lead["Product"] = json.loads(lead["Product"]) if lead["Product"] else []
            lead["Tags"] = json.loads(lead["Tags"]) if lead["Tags"] else []
            lead["SelectedPortfolios"] = json.loads(lead["SelectedPortfolios"]) if lead["SelectedPortfolios"] else []

            leads.append(lead)

        cursor.close()
        conn.close()

        return {"leads": leads}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener los leads: {str(e)}"
        )