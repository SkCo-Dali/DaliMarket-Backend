from fastapi import APIRouter, HTTPException, Query
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


@router.get("/api/leads")
def get_leads(
    name: str = Query(None, description="Filtrar por nombre del lead"),
    email: str = Query(None, description="Filtrar por correo"),
    phone: str = Query(None, description="Filtrar por teléfono"),
    source: str = Query(None, description="Filtrar por fuente"),
    stage: str = Query(None, description="Filtrar por etapa"),
    priority: str = Query(None, description="Filtrar por prioridad"),
    assignedTo: str = Query(None, description="Filtrar por usuario asignado (UUID)"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a devolver")
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = """
            SELECT 
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign, 
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt, 
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, 
                Age, Gender, PreferredContactChannel
            FROM dalilm.Leads            
            WHERE Stage IS NULL OR Stage <> 'Eliminado'
        """
        params = []

        if name:
            query += " AND Name LIKE ?"
            params.append(f"%{name}%")
        if email:
            query += " AND Email LIKE ?"
            params.append(f"%{email}%")
        if phone:
            query += " AND Phone LIKE ?"
            params.append(f"%{phone}%")
        if source:
            query += " AND Source = ?"
            params.append(source)
        if stage:
            query += " AND Stage = ?"
            params.append(stage)
        if priority:
            query += " AND Priority = ?"
            params.append(priority)
        if assignedTo:
            query += " AND AssignedTo = ?"
            params.append(assignedTo)

        query += " ORDER BY CreatedAt DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
        params.extend([skip, limit])

        cursor.execute(query, params)

        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los leads: {str(e)}")
