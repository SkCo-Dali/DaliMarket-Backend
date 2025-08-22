from typing import Dict, List
from application.ports.opportunity_leads_repository import OpportunityLeadsRepositoryPort


class OpportunityLeadsService:
    def __init__(self, repository: OpportunityLeadsRepositoryPort):
        self.repository = repository

    def create_lead(self, lead: Dict) -> Dict:
        return self.repository.insert(lead)

    def list_leads(self) -> List[Dict]:
        return self.repository.get_all()
