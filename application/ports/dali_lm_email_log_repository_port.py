from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_email import DaliLMEmailMessage

class DaliLMEmailLogRepositoryPort(ABC):
    @abstractmethod
    def log_email(
        self,
        email_id: UUID,
        user_id: UUID,
        lead_id: UUID,
        campaign: Optional[str],
        from_email: str,
        to_email: str,
        subject: str,
        html_content: Optional[str],
        plain_content: Optional[str],
        status: str,
        error_message: Optional[str],
    ) -> None:
        """
        Logs an email to the database.
        """
        pass
