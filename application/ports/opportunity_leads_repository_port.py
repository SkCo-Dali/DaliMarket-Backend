# application/ports/opportunity_leads_repository_port.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from domain.models.opportunity_leads import OpportunityLeads


class OpportunityLeadsRepositoryPort(ABC):

    @abstractmethod
    def get_all(self) -> List[OpportunityLeads]:
        pass

    @abstractmethod
    def get_by_agte_id(self, agte_id: int) -> List[OpportunityLeads]:
        pass

    @abstractmethod
    def get_by_opportunity_id_and_agte(self, opportunity_id: int, id_agte: int) -> Optional[OpportunityLeads]:
        """Obtiene un OpportunityLeads desde el repositorio por opportunity_id y idAgte"""
        pass