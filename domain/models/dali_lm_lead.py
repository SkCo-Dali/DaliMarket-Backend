from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

class DaliLML_LeadInput(BaseModel):
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

class DaliLML_Lead(DaliLML_LeadInput):
    id: UUID
