from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class DaliLMInteractionInput(BaseModel):
    LeadId: UUID
    UserId: UUID
    Type: str = Field(..., pattern="^(note|whatsapp|meeting|email|call)$")
    Description: str
    Stage: str = Field(..., max_length=50)
    Outcome: Optional[str] = Field(None, pattern="^(positive|neutral|negative)?$")

class DaliLMInteraction(DaliLMInteractionInput):
    Id: UUID
    CreatedAt: datetime
