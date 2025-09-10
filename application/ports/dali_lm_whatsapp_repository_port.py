from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_whatsapp_template import DaliLMWhatsAppTemplate

class DaliLMWhatsAppRepositoryPort(ABC):
    @abstractmethod
    def get_templates(
        self,
        is_approved: Optional[bool],
        channel_id: Optional[str],
        category: Optional[str],
        language: Optional[str],
    ) -> List[DaliLMWhatsAppTemplate]:
        """
        Gets a list of WhatsApp templates with optional filters.
        """
        pass
