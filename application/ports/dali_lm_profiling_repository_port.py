from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from domain.models.dali_lm_profiling import DaliLMProfilingResult, DaliLMStartProfilingRequest, DaliLMSaveResponseRequest

class DaliLMProfilingRepositoryPort(ABC):
    @abstractmethod
    def check_client_profile(self, email: Optional[str], id_number: Optional[str]) -> Optional[Tuple[UUID, bool]]:
        pass

    @abstractmethod
    def start_profiling(self, request: DaliLMStartProfilingRequest, user_id: Optional[UUID], user_email: str) -> UUID:
        pass

    @abstractmethod
    def save_response(self, request: DaliLMSaveResponseRequest) -> int:
        pass

    @abstractmethod
    def get_profiling_responses(self, profile_id: UUID) -> List[Tuple[str, str]]:
        pass

    @abstractmethod
    def complete_profiling(self, profile_id: UUID, final_type: str, recommended: str, risk: str, strategy: str, result_json: str) -> None:
        pass

    @abstractmethod
    def get_profiling_result(self, profile_id: UUID) -> Optional[DaliLMProfilingResult]:
        pass
