from fastapi import APIRouter, Query
from typing import Optional
from app.repositories.whatsapp_templates_repo import WhatsAppTemplatesRepo

router = APIRouter(prefix="/api/whatsapp/templates", tags=["WhatsApp Templates"])

@router.get("")
def get_templates(
    isApproved: Optional[bool] = Query(None),
    channelId: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    language: Optional[str] = Query(None)
):
    repo = WhatsAppTemplatesRepo()
    templates = repo.get_templates(
        is_approved=isApproved,
        channel_id=channelId,
        category=category,
        language=language
    )
    return {"templates": templates}
