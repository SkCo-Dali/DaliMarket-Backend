from pydantic import BaseModel, EmailStr, field_validator
from fastapi import APIRouter, HTTPException, Path
from uuid import UUID
import pyodbc
import os
import json
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



#  Modelo de entrada
class LeadUpdateInput(BaseModel):
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


@router.put("/api/leads/{id}")
def update_lead(
    id: UUID = Path(..., description="ID del lead en formato UUID"),
    data: dict = None
):
    try:
        lead = LeadUpdateInput(**data)

        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Verificar que el lead exista
        cursor.execute("""
            SELECT 1 FROM dalilm.Leads WHERE Id = ?
        """, str(id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        # Verificar que el usuario asignado exista
        cursor.execute("""
            SELECT 1 FROM dalilm.Users WHERE Id = ?
        """, lead.assignedTo)
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="El usuario asignado no existe.")

        product_json = json.dumps(lead.product) if lead.product else None
        tags_json = json.dumps(lead.tags) if lead.tags else None
        SelectedPortfolios_json = json.dumps(lead.SelectedPortfolios) if lead.SelectedPortfolios else None

        cursor.execute("""
            UPDATE dalilm.Leads
            SET 
                CreatedBy = ?, Name = ?, Email = ?, Phone = ?, DocumentNumber = ?, Company = ?, 
                Source = ?, Campaign = ?, Product = ?, Stage = ?, Priority = ?, 
                Value = ?, AssignedTo = ?, NextFollowUp = ?, Notes = ?, Tags = ?, 
                DocumentType = ?, SelectedPortfolios = ?, CampaignOwnerName = ?, Age = ?, Gender = ?, PreferredContactChannel = ?,
                UpdatedAt = GETUTCDATE()
            WHERE Id = ?
        """, lead.CreatedBy, lead.name, lead.email, lead.phone, lead.documentNumber, lead.company,
             lead.source, lead.campaign, product_json, lead.stage, lead.priority,
             lead.value, lead.assignedTo, lead.nextFollowUp, lead.notes, tags_json, 
             lead.DocumentType, SelectedPortfolios_json, lead.CampaignOwnerName, lead.Age, 
             lead.Gender, lead.PreferredContactChannel, str(id))

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "Lead actualizado exitosamente."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar lead: {str(e)}")
