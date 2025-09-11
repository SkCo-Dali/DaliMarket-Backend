from fastapi import APIRouter, Depends, HTTPException
from typing import List

from application.services.dali_lm_interaction_service import DaliLMInteractionService
from domain.models.dali_lm_interaction import DaliLMInteraction, DaliLMInteractionInput
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.repositories.dali_lm_interaction_repository import DaliLMInteractionRepository

router = APIRouter(prefix="/dalilm/interactions", tags=["DaliLM Interactions"])

def get_dali_lm_interaction_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
) -> DaliLMInteractionService:
    repo = DaliLMInteractionRepository(sql)
    return DaliLMInteractionService(repo)

from uuid import UUID

@router.get("/by-lead/{lead_id}", response_model=List[DaliLMInteraction])
def get_interactions_by_lead(
    lead_id: UUID,
    service: DaliLMInteractionService = Depends(get_dali_lm_interaction_service),
):
    """
    Gets all interactions for a given lead.
    """
    return service.get_interactions_by_lead(lead_id)

from pydantic import BaseModel

class InteractionUpdate(BaseModel):
    Type: Optional[str] = Field(None, pattern="^(note|whatsapp|meeting|email|call)$")
    Description: Optional[str] = None
    UserId: Optional[UUID] = None
    Outcome: Optional[str] = Field(None, pattern="^(positive|neutral|negative)?$")
    Stage: Optional[str] = None

@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(
    interaction_id: UUID,
    service: DaliLMInteractionService = Depends(get_dali_lm_interaction_service),
):
    """
    Deletes an interaction.
    """
    service.delete_interaction(interaction_id)
    return

@router.put("/{interaction_id}", response_model=DaliLMInteraction)
def update_interaction(
    interaction_id: UUID,
    interaction_data: InteractionUpdate,
    service: DaliLMInteractionService = Depends(get_dali_lm_interaction_service),
):
    """
    Updates an interaction with partial data.
    """
    update_data = interaction_data.model_dump(exclude_unset=True)
    return service.update_interaction(interaction_id, update_data)

@router.post("/", response_model=DaliLMInteraction)
def create_interaction(
    interaction_data: DaliLMInteractionInput,
    service: DaliLMInteractionService = Depends(get_dali_lm_interaction_service),
):
    """
    Creates a new interaction.
    """
    try:
        return service.create_interaction(interaction_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
