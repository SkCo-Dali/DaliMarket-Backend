from typing import List, Optional
from uuid import UUID
from domain.models.dali_lm_whatsapp_template import DaliLMWhatsAppTemplate
from application.ports.dali_lm_whatsapp_repository_port import DaliLMWhatsAppRepositoryPort

class DaliLMWhatsAppService:
    def __init__(self, repository: DaliLMWhatsAppRepositoryPort):
        self.repository = repository

    def get_templates(
        self,
        is_approved: Optional[bool],
        channel_id: Optional[str],
        category: Optional[str],
        language: Optional[str],
    ) -> List[DaliLMWhatsAppTemplate]:
        return self.repository.get_templates(is_approved, channel_id, category, language)
