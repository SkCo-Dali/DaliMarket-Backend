# application/services/opportunity_detail_service.py
from typing import Dict, List, Optional
from application.ports.opportunity_detail_repository_port import OpportunityDetailRepositoryPort
from domain.models.opportunity_detail import OpportunityDetail


class OpportunityDetailService:
    def __init__(self, repository: OpportunityDetailRepositoryPort):
        self.repository = repository

    def list_details(self) -> List[OpportunityDetail]:
        return self.repository.get_all()
    
    def get_detail_by_opportunity_id(self, opportunity_id: str) -> Optional[OpportunityDetail]:
        return self.repository.get_by_opportunity_id(opportunity_id)

