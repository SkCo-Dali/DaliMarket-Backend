# application/ports/opportunity_leads_repository_port.py
from abc import ABC, abstractmethod
from typing import Dict, List

from domain.models.opportunity_leads import OpportunityLeads


class OpportunityLeadsRepositoryPort(ABC):

    @abstractmethod
    def get_all(self) -> List[OpportunityLeads]:
        pass

    @abstractmethod
    def get_by_agte_id(self, agte_id: int) -> List[OpportunityLeads]:
        pass