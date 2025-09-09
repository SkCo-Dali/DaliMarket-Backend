from fastapi import APIRouter, HTTPException, Response, Query
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv
import io
import csv
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


@router.get("/api/leads/export")
def export_leads(
    assignedTo: UUID | None = Query(None, description="Filtrar por usuario asignado (opcional)"),
    CreatedBy: UUID | None = Query(None, description="Filtrar por usuario de creación del lead (opcional)"),
    stage: str | None = Query(None, description="Filtrar por etapa (opcional)"),
    priority: str | None = Query(None, description="Filtrar por prioridad (opcional)")
):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Construir consulta dinámica
        query = """
            SELECT CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                   Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                   NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, 
                   Age, Gender, PreferredContactChannel
            FROM dalilm.Leads
            WHERE Stage IS NULL OR Stage <> 'Eliminado'
        """
        params = []

        if assignedTo:
            query += " AND AssignedTo = ?"
            params.append(str(assignedTo))
        if CreatedBy:
            query += " AND CreatedBy = ?"
            params.append(str(CreatedBy))
        if stage:
            query += " AND Stage = ?"
            params.append(stage)
        if priority:
            query += " AND Priority = ?"
            params.append(priority)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        if not rows:
            raise HTTPException(status_code=404, detail="No se encontraron leads con esos filtros.")

        # Crear CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # Escribir encabezados
        writer.writerow(columns)

        # Escribir datos
        for row in rows:
            row_dict = dict(zip(columns, row))
            # Convertir campos JSON a string
            row_dict["Product"] = json.dumps(row_dict["Product"]) if row_dict["Product"] else "[]"
            row_dict["Tags"] = json.dumps(row_dict["Tags"]) if row_dict["Tags"] else "[]"
            row_dict["SelectedPortfolios"] = json.dumps(row_dict["SelectedPortfolios"]) if row_dict["SelectedPortfolios"] else "[]"

            writer.writerow([row_dict.get(col) for col in columns])

        cursor.close()
        conn.close()

        headers = {
            "Content-Disposition": "attachment; filename=leads_export.csv"
        }

        return Response(content=output.getvalue(), media_type="text/csv", headers=headers)

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar leads: {str(e)}")
