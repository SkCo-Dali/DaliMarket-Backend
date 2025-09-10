from fastapi import HTTPException
from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_lead_assignment import DaliLMLeadAssignment
from application.ports.dali_lm_lead_assignment_repository_port import DaliLMLeadAssignmentRepositoryPort

class DaliLMLeadAssignmentService:
    def __init__(self, repository: DaliLMLeadAssignmentRepositoryPort):
        self.repository = repository

    def get_current_assignments_by_user(self, user_id: UUID) -> List[DaliLMLeadAssignment]:
        return self.repository.get_current_assignments_by_user(user_id)
