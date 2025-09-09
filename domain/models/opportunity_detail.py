from typing import List, Optional
from pydantic import BaseModel

class OpportunityDetail(BaseModel):
    OpportunityId: int
    Title: str
    Subtitle: str
    Description: str
    EmailTemplate: str
    DaliPrompt: str
    Categories: List[str]