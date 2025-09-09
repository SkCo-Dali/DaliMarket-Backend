from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
import pyodbc
import os
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

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

class LeadOut(BaseModel):
    CreatedBy: Optional[str]
    Id: Optional[str]
    Name: Optional[str]
    Email: Optional[str]
    Phone: Optional[str]
    DocumentNumber: Optional[str]
    Company: Optional[str]
    Source: Optional[str]
    Campaign: Optional[str]
    Product: Optional[str]
    Stage: Optional[str]
    Priority: Optional[str]
    Value: Optional[str]
    AssignedTo: Optional[str]
    CreatedAt: Optional[str]
    UpdatedAt: Optional[str]
    NextFollowUp: Optional[str]
    Notes: Optional[str]
    Tags: Optional[str]
    DocumentType: Optional[str]
    SelectedPortfolios: Optional[str]
    CampaignOwnerName: Optional[str]
    Age: Optional[str]
    Gender: Optional[str]
    PreferredContactChannel: Optional[str]
    AdditionalInfo: Optional[str]

@router.get("/api/lead-assignments/reassignable/{user_id}", response_model=List[LeadOut])
def get_reassignable_leads(user_id: str):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            # Obtener el rol del usuario
            cursor.execute("SELECT Role FROM dalilm.Users WHERE Id = ?", user_id)
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            role = row[0].lower()

            # Determinar query según el rol
            if role in ["admin", "supervisor"]:
                query = "SELECT * FROM dalilm.Leads where Stage <> 'Eliminado'"
                cursor.execute(query)
            elif role in ["gestor", "director", "socio"]:
                query = """
                    SELECT DISTINCT l.*
                    FROM dalilm.Leads l
                    LEFT JOIN dalilm.LeadAssignmentHistory lah ON l.Id = lah.LeadId
                    WHERE l.AssignedTo = ? OR lah.AssignedBy = ? and l.Stage <> 'Eliminado'
                """
                cursor.execute(query, user_id, user_id)
            elif role in ["fp"]:
                query = """
                    SELECT *
                    FROM dalilm.Leads l
                    WHERE l.AssignedTo = ? and l.Stage <> 'Eliminado'
                """
                cursor.execute(query, user_id)
            else:
                return []

            # Procesar resultados
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = []

            for row in rows:
                record = dict(zip(columns, row))
                # Convertir a string los valores que FastAPI no puede serializar automáticamente
                for k, v in record.items():
                    if isinstance(v, (datetime, Decimal, int, float)):
                        record[k] = str(v)
                    elif v is None:
                        record[k] = None
                    else:
                        record[k] = str(v)  # Por seguridad convertir todos los valores a str

                results.append({
                    "CreatedBy": record.get("CreatedBy"),
                    "Id": record.get("Id"),
                    "Name": record.get("Name"),
                    "Email": record.get("Email"),
                    "Phone": record.get("Phone"),
                    "DocumentNumber": record.get("DocumentNumber"),
                    "Company": record.get("Company"),
                    "Source": record.get("Source"),
                    "Campaign": record.get("Campaign"),
                    "Product": record.get("Product"),
                    "Stage": record.get("Stage"),
                    "Priority": record.get("Priority"),
                    "Value": record.get("Value"),
                    "AssignedTo": record.get("AssignedTo"),
                    "CreatedAt": record.get("CreatedAt"),
                    "UpdatedAt": record.get("UpdatedAt"),
                    "NextFollowUp": record.get("NextFollowUp"),
                    "Notes": record.get("Notes"),
                    "Tags": record.get("Tags"),
                    "DocumentType": record.get("DocumentType"),
                    "SelectedPortfolios": record.get("SelectedPortfolios"),
                    "CampaignOwnerName": record.get("CampaignOwnerName"),
                    "Age": record.get("Age"),
                    "Gender": record.get("Gender"),
                    "PreferredContactChannel": record.get("PreferredContactChannel"),
                    "AdditionalInfo": record.get("AdditionalInfo")
                })

            return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
