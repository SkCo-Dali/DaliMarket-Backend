# application/ports/opportunity_detail_repository.py
from abc import ABC, abstractmethod
from typing import Dict, List


class OpportunityDetailRepositoryPort(ABC):

    @abstractmethod
    def get_all(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_by_opportunity_id(self, opportunity_id: str) -> Dict:
        pass
