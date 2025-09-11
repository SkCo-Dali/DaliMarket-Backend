from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.dali_lm_user import DaliLMUser, DaliLMUserInput
from uuid import UUID

class DaliLMUserRepositoryPort(ABC):
    @abstractmethod
    def create_user(self, user_data: DaliLMUserInput) -> DaliLMUser:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[DaliLMUser]:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[DaliLMUser]:
        pass

    @abstractmethod
    def delete_user(self, user_id: UUID) -> None:
        pass

    @abstractmethod
    def get_user_roles(self) -> List[str]:
        pass

    @abstractmethod
    def list_users(self, name: Optional[str], email: Optional[str], role: Optional[str], is_active: Optional[bool], skip: int, limit: int) -> List[DaliLMUser]:
        pass

    @abstractmethod
    def search_users(self, query: str) -> List[DaliLMUser]:
        pass

    @abstractmethod
    def set_user_status(self, user_id: UUID, is_active: bool) -> None:
        pass

    @abstractmethod
    def update_user(self, user_id: UUID, user_data: DaliLMUserInput) -> DaliLMUser:
        pass
