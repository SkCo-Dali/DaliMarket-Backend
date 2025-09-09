from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import pyodbc
import os
from dotenv import load_dotenv
from datetime import datetime

# Cargar variables de entorno
load_dotenv()

router = APIRouter()

# Conexión a SQL Server
connection_string = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('SQL_SERVER')};DATABASE={os.getenv('SQL_DATABASE')};"
    f"UID={os.getenv('SQL_USERNAME')};PWD={os.getenv('SQL_PASSWORD')}"
)

# Modelos de respuesta
class Interaction(BaseModel):
    Id: str
    LeadId: str
    Type: str
    Description: str
    UserName: str
    Outcome: Optional[str]
    Stage: Optional[str]
    CreatedAt: datetime

class LeadWithInteractions(BaseModel):
    LeadId: str
    Name: str
    Email: Optional[str]
    DocumentType: Optional[str]
    DocumentNumber: Optional[str]
    Campaign: Optional[str]
    CreatedAt: datetime
    Interactions: List[Interaction]

@router.get("/api/client-history", response_model=List[LeadWithInteractions])
def get_client_history(
    email: Optional[str] = Query(None),
    DocumentType: Optional[str] = Query(None),
    DocumentNumber: Optional[str] = Query(None)
):
    if not email and not (DocumentType and DocumentNumber):
        raise HTTPException(status_code=400, detail="Debe proporcionar al menos el Email o DocumentType y DocumentNumber.")

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Buscar leads por email o documento
        query = """
            SELECT Id, Name, Email, DocumentType, DocumentNumber, Campaign, CreatedAt
            FROM dalilm.Leads
            WHERE 1=0
        """
        params = []

        if email:
            query += " OR Email = ?"
            params.append(email)

        if DocumentType and DocumentNumber:
            query += " OR (DocumentType = ? AND DocumentNumber = ?)"
            params.extend([DocumentType, DocumentNumber])

        cursor.execute(query, params)
        leads = cursor.fetchall()

        result = []
        for lead in leads:
            lead_id = str(lead.Id)

            # Buscar interacciones del lead
            cursor.execute("""
                SELECT i.Id, i.LeadId, i.Type, i.Description, i.UserId, u.Name AS UserName, i.Outcome, i.Stage, i.CreatedAt
                FROM dalilm.Interactions i
                JOIN dalilm.Users u ON i.UserId = u.Id
                WHERE i.LeadId = ?
            """, lead_id)
            interactions = cursor.fetchall()

            result.append(LeadWithInteractions(
                LeadId=lead_id,
                Name=lead.Name,
                Email=lead.Email,
                DocumentType=lead.DocumentType,
                DocumentNumber=str(lead.DocumentNumber) if lead.DocumentNumber is not None else None,
                Campaign=lead.Campaign,
                CreatedAt=lead.CreatedAt,
                Interactions=[
                    Interaction(
                        Id=str(i.Id),
                        LeadId=str(i.LeadId),
                        Type=i.Type,
                        Description=i.Description,
                        UserId=str(i.UserId),
                        UserName=i.UserName,
                        Outcome=i.Outcome,
                        Stage=i.Stage,
                        CreatedAt=i.CreatedAt
                    )
                    for i in interactions
                ]
            ))

        cursor.close()
        conn.close()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
