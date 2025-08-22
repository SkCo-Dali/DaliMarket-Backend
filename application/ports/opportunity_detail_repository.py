from abc import ABC, abstractmethod
from typing import Dict, List


class OpportunityDetailRepositoryPort(ABC):
    @abstractmethod
    def insert(self, detail: Dict) -> Dict:
        pass

    @abstractmethod
    def get_all(self) -> List[Dict]:
        pass
