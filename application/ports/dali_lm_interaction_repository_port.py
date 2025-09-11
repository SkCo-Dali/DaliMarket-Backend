from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_interaction import DaliLMInteraction, DaliLMInteractionInput

class DaliLMInteractionRepositoryPort(ABC):
    @abstractmethod
    def create_interaction(self, interaction_data: DaliLMInteractionInput) -> DaliLMInteraction:
        """
        Creates a new interaction in the database.
        """
        pass

    @abstractmethod
    def get_interactions_by_lead(self, lead_id: UUID) -> List[DaliLMInteraction]:
        """
        Gets all interactions for a given lead.
        """
        pass

    @abstractmethod
    def update_interaction(self, interaction_id: UUID, interaction_data: dict) -> DaliLMInteraction:
        """
        Updates an interaction with partial data.
        """
        pass

    @abstractmethod
    def get_interaction_by_id(self, interaction_id: UUID) -> Optional[DaliLMInteraction]:
        """
        Gets an interaction by its ID.
        """
        pass

    @abstractmethod
    def delete_interaction(self, interaction_id: UUID) -> None:
        """
        Deletes an interaction.
        """
        pass
