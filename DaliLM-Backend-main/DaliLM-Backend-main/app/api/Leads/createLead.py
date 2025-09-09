from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any
import pyodbc
import os
from dotenv import load_dotenv
from uuid import uuid4
import json

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

# Modelo de entrada para crear lead
class LeadInput(BaseModel):
    CreatedBy: str
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    documentNumber: int | None = None
    company: str | None = None
    source: str
    campaign: str | None = None
    product: list | None = None
    stage: str
    priority: str 
    value: float = 0
    assignedTo: str
    nextFollowUp: str | None = None
    notes: str | None = None
    tags: list | None = None
    DocumentType: str | None = None
    SelectedPortfolios: list | None = None
    CampaignOwnerName: str | None = None
    Age: int | None = None
    Gender: str | None = None
    PreferredContactChannel: str | None = None
    AdditionalInfo: Optional[Dict[str, Any]] = None

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v


    @field_validator("priority")
    def validate_priority(cls, v):
        allowed_priorities = ['Baja', 'Media', 'Alta', 'Urgente']
        if v not in allowed_priorities:
            raise ValueError(f"La prioridad '{v}' no es válida.")
        return v


# Endpoint POST /api/leads
@router.post("/api/leads")
def create_lead(data: dict):
    try:
        lead = LeadInput(**data)

        lead_id = str(uuid4())
        product_json = json.dumps(lead.product) if lead.product else None
        tags_json = json.dumps(lead.tags) if lead.tags else None
        SelectedPortfolios_json = json.dumps(lead.SelectedPortfolios) if lead.SelectedPortfolios else None
        additional_info_json = json.dumps(lead.AdditionalInfo) if lead.AdditionalInfo else None

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar si el usuario asignado existe
        cursor.execute("""
            SELECT 1 FROM dalilm.Users WHERE Id = ?
        """, lead.assignedTo)
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="El usuario asignado no existe.")

        # Insertar en Leads
        cursor.execute("""
            INSERT INTO dalilm.Leads (
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, Age, Gender, 
                PreferredContactChannel, AdditionalInfo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETUTCDATE(), GETUTCDATE(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, lead.CreatedBy, lead_id, lead.name, lead.email, lead.phone, lead.documentNumber, lead.company,
             lead.source, lead.campaign, product_json, lead.stage, lead.priority, lead.value,
             lead.assignedTo, lead.nextFollowUp, lead.notes, tags_json,lead.DocumentType, SelectedPortfolios_json, 
             lead.CampaignOwnerName, lead.Age, lead.Gender, lead.PreferredContactChannel, additional_info_json)

        # ✔️ Insertar en LeadsRaw una copia exacta
        cursor.execute("""
            INSERT INTO dalilm.LeadsRaw (
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, Age, Gender, 
                PreferredContactChannel, AdditionalInfo
            )
            SELECT 
                CreatedBy, Id, Name, Email, Phone, DocumentNumber, Company, Source, Campaign,
                Product, Stage, Priority, Value, AssignedTo, CreatedAt, UpdatedAt,
                NextFollowUp, Notes, Tags, DocumentType, SelectedPortfolios, CampaignOwnerName, Age, Gender, 
                PreferredContactChannel, AdditionalInfo
            FROM dalilm.Leads
            WHERE Id = ?
        """, lead_id)

        conn.commit()
        cursor.close()
        conn.close()

        return {
            "message": "Lead creado exitosamente.",
            "lead": {
                "CreatedBy": lead.CreatedBy,
                "id": lead_id,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "documentNumber": lead.documentNumber,
                "company": lead.company,
                "source": lead.source,
                "campaign": lead.campaign,
                "product": lead.product,
                "stage": lead.stage,
                "priority": lead.priority,
                "value": lead.value,
                "assignedTo": lead.assignedTo,
                "nextFollowUp": lead.nextFollowUp,
                "notes": lead.notes,
                "tags": lead.tags,
                "DocumentType": lead.DocumentType,
                "SelectedPortfolios": lead.SelectedPortfolios,
                "CampaignOwnerName": lead.CampaignOwnerName,
                "Age": lead.Age,
                "Gender": lead.Gender,
                "PreferredContactChannel": lead.PreferredContactChannel,
                "AdditionalInfo": lead.AdditionalInfo
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear lead: {str(e)}")

