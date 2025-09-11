from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID

from application.services.dali_lm_lead_assignment_service import DaliLMLeadAssignmentService
from domain.models.dali_lm_lead_assignment import DaliLMLeadAssignment
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.repositories.dali_lm_lead_assignment_repository import DaliLMLeadAssignmentRepository

router = APIRouter(prefix="/dalilm/lead-assignments", tags=["DaliLM Lead Assignments"])

def get_dali_lm_lead_assignment_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
) -> DaliLMLeadAssignmentService:
    repo = DaliLMLeadAssignmentRepository(sql)
    return DaliLMLeadAssignmentService(repo)

@router.get("/user/{user_id}/current", response_model=List[DaliLMLeadAssignment])
def get_current_assignments_by_user(
    user_id: UUID,
    service: DaliLMLeadAssignmentService = Depends(get_dali_lm_lead_assignment_service),
):
    """
    Gets the current lead assignments for a user.
    """
    return service.get_current_assignments_by_user(user_id)
