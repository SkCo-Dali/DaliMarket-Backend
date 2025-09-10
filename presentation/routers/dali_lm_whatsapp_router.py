from fastapi import APIRouter, Depends, Query
from typing import List, Optional

from application.services.dali_lm_whatsapp_service import DaliLMWhatsAppService
from domain.models.dali_lm_whatsapp_template import DaliLMWhatsAppTemplate
from infrastructure.adapters.sql_server_adapter import SqlServerAdapter, get_sql_server_session
from infrastructure.repositories.dali_lm_whatsapp_repository import DaliLMWhatsAppRepository

router = APIRouter(prefix="/dalilm/whatsapp/templates", tags=["DaliLM WhatsApp"])

def get_dali_lm_whatsapp_service(
    sql: SqlServerAdapter = Depends(get_sql_server_session),
) -> DaliLMWhatsAppService:
    repo = DaliLMWhatsAppRepository(sql)
    return DaliLMWhatsAppService(repo)

@router.get("/", response_model=List[DaliLMWhatsAppTemplate])
def get_templates(
    isApproved: Optional[bool] = Query(None),
    channelId: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    service: DaliLMWhatsAppService = Depends(get_dali_lm_whatsapp_service),
):
    """
    Gets a list of WhatsApp templates with optional filters.
    """
    return service.get_templates(isApproved, channelId, category, language)
