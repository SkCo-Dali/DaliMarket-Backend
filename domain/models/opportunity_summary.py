from typing import List, Optional
from pydantic import BaseModel

from domain.models.opportunity_lead import OpportunityLead


class OpportunitySummary(BaseModel):
    OpportunityId: int
    Priority: int
    lead_count: int
    Title: str
    Subtitle: str
    Description: str
    Categories: List[str]