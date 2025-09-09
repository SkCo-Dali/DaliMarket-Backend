# application/services/opportunity_leads_service.py
from typing import Dict, List
from application.ports.opportunity_leads_repository_port import OpportunityLeadsRepositoryPort
from domain.models.opportunity_leads import OpportunityLeads


class OpportunityLeadsService:
    def __init__(self, repository: OpportunityLeadsRepositoryPort):
        self.repository = repository

    def list_leads(self) -> List[OpportunityLeads]:
        return self.repository.get_all()
    
    def get_leads_by_agte_id(self, agte_id: str) -> List[OpportunityLeads]:
        return self.repository.get_by_agte_id(agte_id)
