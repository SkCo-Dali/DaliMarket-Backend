# app/services/send_service.py
import uuid
from fastapi import BackgroundTasks
from typing import List
from app.integrations.botmaker_client import BotmakerClient
from app.repositories.whatsapp_batches_repo import WhatsAppBatchesRepo
from app.repositories.whatsapp_sendlogs_repo import WhatsAppSendLogsRepo
from app.repositories.whatsapp_idempotency_repo import WhatsAppIdempotencyRepo
from app.models.whatsapp import LeadMessage

async def process_batch_async(batch_id, user_id, template_id, ChannelId, WhatsAppTemplateName, leads, idempotency_key: str | None = None):
    bot = BotmakerClient()
    batches_repo = WhatsAppBatchesRepo()
    logs_repo = WhatsAppSendLogsRepo()


    print(f"Se inició el envío en Botmaker")
    success = 0
    failed = 0

    for lead in leads:
        try:
            contacts = [{
                "contactId": lead.contactId,
                "variables": lead.variables
                }]
            print(f"channel_id={str(ChannelId)}, intentIdOrName: {str(WhatsAppTemplateName)}, contacts: {contacts}")
            resp = await bot.send_notification(
                campaign="Dali_FPs",
                channel_id=str(ChannelId),
                name="jcoronado@skandia.com.co",
                intentIdOrName=str(WhatsAppTemplateName),
                contacts=contacts
            )
            
            message_id = resp
            logs_repo.create_log(
                batch_id=str(batch_id),
                user_id=user_id,
                lead_id=lead.leadId,
                recipient_number=lead.contactId,
                recipient_name=lead.name,
                template_id=str(template_id),
                message_content=str(lead.variables),
                message_id=str(message_id),
                status="SENT"
            )
            success += 1
        except Exception as e:
            logs_repo.create_log(
                batch_id=str(batch_id),
                user_id=user_id,
                lead_id=lead.leadId,
                recipient_number=lead.contactId,
                recipient_name=lead.name,
                template_id=str(template_id),
                message_content=str(lead.variables),
                message_id=None,
                status="FAILED",
                failure_reason=str(e)
            )
            failed += 1

    status = "COMPLETED" if failed == 0 else ("FAILED" if success == 0 else "COMPLETED")
    batches_repo.update_batch_counts(batch_id, success, failed, status)
    if idempotency_key:
        WhatsAppIdempotencyRepo().mark_completed_mass(idempotency_key, str(batch_id))
