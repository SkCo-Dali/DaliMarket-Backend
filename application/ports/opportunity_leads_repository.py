from abc import ABC, abstractmethod
from typing import Dict, List


class OpportunityLeadsRepositoryPort(ABC):
    @abstractmethod
    def insert(self, lead: Dict) -> Dict:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict]:
        pass

    @abstractmethod
    def get_by_agte_id(self, agte_id: str) -> List[Dict]:
        pass
