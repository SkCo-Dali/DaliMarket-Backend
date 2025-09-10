from fastapi import HTTPException
from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_interaction import DaliLMInteraction, DaliLMInteractionInput
from application.ports.dali_lm_interaction_repository_port import DaliLMInteractionRepositoryPort

class DaliLMInteractionService:
    def __init__(self, interaction_repository: DaliLMInteractionRepositoryPort):
        self.interaction_repository = interaction_repository

    def create_interaction(self, interaction_data: DaliLMInteractionInput) -> DaliLMInteraction:
        return self.interaction_repository.create_interaction(interaction_data)

    def get_interactions_by_lead(self, lead_id: UUID) -> List[DaliLMInteraction]:
        return self.interaction_repository.get_interactions_by_lead(lead_id)

    def update_interaction(self, interaction_id: UUID, interaction_data: dict) -> DaliLMInteraction:
        if not interaction_data:
            raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
        return self.interaction_repository.update_interaction(interaction_id, interaction_data)

    def delete_interaction(self, interaction_id: UUID) -> None:
        self.interaction_repository.delete_interaction(interaction_id)
