from typing import Any, Optional, Dict
from pydantic import BaseModel, field_validator


class Lead(BaseModel):
    CreatedBy: str
    name: str
    email: str | None = None # Corregir
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