from fastapi import APIRouter, HTTPException
import pyodbc
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from decimal import Decimal
from datetime import datetime

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

# Función para convertir Decimals y datetime
def convert_to_serializable(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


@router.get("/api/leads/duplicates")
def detect_duplicates():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        query = """
        WITH LeadDuplicates AS (
            SELECT 
                Email,
                Phone,
                DocumentNumber,
                COUNT(*) AS Count
            FROM dalilm.Leads
            WHERE 
                Email IS NOT NULL OR
                Phone IS NOT NULL OR
                DocumentNumber IS NOT NULL
            GROUP BY 
                Email,
                Phone,
                DocumentNumber
            HAVING COUNT(*) > 1
        )
        SELECT 
            l.CreatedBy,
            l.Id,
            l.Name,
            l.Email,
            l.Phone,
            l.DocumentNumber,
            l.Company,
            l.Source,
            l.Campaign,
            l.Product,
            l.Stage,
            l.Priority,
            l.Value,
            l.AssignedTo,
            l.CreatedAt,
            l.UpdatedAt,
            l.NextFollowUp,
            l.Notes,
            l.Tags,
            l.DocumentType,
            l.SelectedPortfolios,
            l.CampaignOwnerName,
            l.Age,
            l.Gender,
            l.PreferredContactChannel
        FROM dalilm.Leads l
        INNER JOIN LeadDuplicates d
            ON (l.Email = d.Email AND l.Email IS NOT NULL)
            OR (l.Phone = d.Phone AND l.Phone IS NOT NULL)
            OR (l.DocumentNumber = d.DocumentNumber AND l.DocumentNumber IS NOT NULL)
        ORDER BY l.Email, l.Phone, l.DocumentNumber
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        results = []
        for row in rows:
            result = {column: convert_to_serializable(value) for column, value in zip(columns, row)}
            results.append(result)

        cursor.close()
        conn.close()

        return JSONResponse(content=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al detectar duplicados: {str(e)}")
