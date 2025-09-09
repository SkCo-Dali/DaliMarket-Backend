# application/ports/opportunity_detail_repository_port.py
from abc import ABC, abstractmethod
from typing import Dict, List

from domain.models.opportunity_detail import OpportunityDetail


class OpportunityDetailRepositoryPort(ABC):

    @abstractmethod
    def get_all(self) -> List[OpportunityDetail]:
        pass

    @abstractmethod
    def get_by_opportunity_id(self, opportunity_id: int) -> OpportunityDetail:
        pass
