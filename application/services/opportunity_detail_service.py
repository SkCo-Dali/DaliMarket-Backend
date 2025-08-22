from typing import Dict, List
from application.ports.opportunity_detail_repository import OpportunityDetailRepositoryPort


class OpportunityDetailService:
    def __init__(self, repository: OpportunityDetailRepositoryPort):
        self.repository = repository

    def create_detail(self, detail: Dict) -> Dict:
        return self.repository.insert(detail)

    def list_details(self) -> List[Dict]:
        return self.repository.get_all()
