from abc import ABC, abstractmethod
from domain.models.dali_lm_lead import DaliLML_Lead, DaliLML_LeadInput

from uuid import UUID
from typing import Optional

class DaliLMLeadRepositoryPort(ABC):
    @abstractmethod
    def create_lead(self, lead_data: DaliLML_LeadInput) -> DaliLML_Lead:
        """
        Creates a new lead in the database.
        """
        pass

from typing import List

    @abstractmethod
    def get_lead_by_id(self, lead_id: UUID) -> Optional[DaliLML_Lead]:
        """
        Gets a lead by its ID.
        """
        pass

    @abstractmethod
    def list_leads(
        self,
        name: Optional[str],
        email: Optional[str],
        phone: Optional[str],
        source: Optional[str],
        stage: Optional[str],
        priority: Optional[str],
        assigned_to: Optional[str],
        skip: int,
        limit: int,
    ) -> List[DaliLML_Lead]:
        """
        Lists leads with filtering and pagination.
        """
        pass

    @abstractmethod
    def update_lead(self, lead_id: UUID, lead_data: DaliLML_LeadInput) -> DaliLML_Lead:
        """
        Updates a lead.
        """
        pass

    @abstractmethod
    def delete_lead(self, lead_id: UUID) -> None:
        """
        Deletes a lead (soft delete).
        """
        pass

    @abstractmethod
    def get_leads_by_user(self, user_id: UUID, stage: Optional[str], priority: Optional[str]) -> List[DaliLML_Lead]:
        """
        Gets leads assigned to a specific user.
        """
        pass

    @abstractmethod
    def assign_lead(self, lead_id: UUID, user_id: UUID) -> None:
        """
        Assigns a lead to a user.
        """
        pass

    @abstractmethod
    def update_lead_stage(self, lead_id: UUID, stage: str) -> None:
        """
        Updates the stage of a lead.
        """
        pass

    @abstractmethod
    def get_duplicate_leads(self) -> List[DaliLML_Lead]:
        """
        Gets a list of duplicate leads.
        """
        pass

    @abstractmethod
    def merge_leads(self, lead_ids: List[UUID], primary_lead_id: UUID) -> None:
        """
        Merges a list of leads into a primary lead.
        """
        pass

    @abstractmethod
    def bulk_assign_leads(self, lead_ids: List[UUID], user_id: UUID) -> None:
        """
        Assigns a list of leads to a user.
        """
        pass

    @abstractmethod
    def export_leads(
        self,
        assigned_to: Optional[UUID],
        created_by: Optional[UUID],
        stage: Optional[str],
        priority: Optional[str],
    ) -> List[DaliLML_Lead]:
        """
        Exports a filtered list of leads.
        """
        pass

    @abstractmethod
    def bulk_lead_file(self, leads_data: List[tuple]) -> Tuple[int, List[dict]]:
        """
        Inserts a batch of leads from a file.
        Returns the number of inserted rows and a list of errors.
        """
        pass
