from typing import List, Optional
from pydantic import BaseModel

from domain.models.opportunity_lead import OpportunityLead


class OpportunityLeads(BaseModel):
    OpportunityId: int
    Beggining: str 
    End: str
    IdAgte: int
    IdSociedad: int
    WSaler: str
    Status: int
    Priority: int
    leads: List[OpportunityLead]