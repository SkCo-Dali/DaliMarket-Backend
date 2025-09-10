from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class DaliLMLeadAssignment(BaseModel):
    LeadId: UUID
    LeadName: str
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Stage: Optional[str] = None
    Priority: Optional[str] = None
    Value: Optional[float] = None
    Source: Optional[str] = None
    Campaign: Optional[str] = None
    CreatedAt: datetime
    AssignedAt: datetime
