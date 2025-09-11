from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class DaliLMWhatsAppTemplate(BaseModel):
    Id: UUID
    Name: str
    Content: str
    Variables: Optional[str] = None # JSON string
    IsApproved: bool
    WhatsAppTemplateId: Optional[str] = None
    Language: Optional[str] = None
    Category: Optional[str] = None
    CreatedAt: datetime
    UpdatedAt: datetime
    ChannelId: Optional[str] = None
