from fastapi import APIRouter, HTTPException, Path
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv

# Cargar .env
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


@router.get("/api/leads/{id}")
def get_lead_by_id(id: UUID = Path(..., description="ID del lead en formato UUID")):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign, 
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt, 
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, 
                Age, Gender, PreferredContactChannel, AdditionalInfo
            FROM dalilm.Leads
            WHERE (Stage IS NULL OR Stage <> 'Eliminado') and Id = ?
        """, str(id))

        row = cursor.fetchone()

        columns = [column[0] for column in cursor.description] if row else []

        cursor.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        lead = dict(zip(columns, row))

        return lead

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el lead: {str(e)}")
