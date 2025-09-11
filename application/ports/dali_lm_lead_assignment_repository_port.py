from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_lead_assignment import DaliLMLeadAssignment

class DaliLMLeadAssignmentRepositoryPort(ABC):
    @abstractmethod
    def get_current_assignments_by_user(self, user_id: UUID) -> List[DaliLMLeadAssignment]:
        """
        Gets the current lead assignments for a given user.
        """
        pass
