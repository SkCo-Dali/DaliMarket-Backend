from fastapi import APIRouter, Request, HTTPException
from app.repositories.whatsapp_sendlogs_repo import WhatsAppSendLogsRepo
from app.repositories.whatsapp_messageevents_repo import WhatsAppMessageEventsRepo
from app.repositories.whatsapp_templates_repo import WhatsAppTemplatesRepo
from app.repositories.users_repo import UsersRepo
from app.integrations.cosmos_client import CosmosAnalyticsClient
from app.integrations.botmaker_client import BotmakerClient
from app.utils.whatsapp import first_name, build_wa_me_link
from datetime import datetime

router = APIRouter(prefix="/api/whatsapp/webhooks", tags=["WhatsApp Webhooks"])

def _save_event_and_cosmos(payload: dict, event_type: str, log: dict,
                           cosmos: CosmosAnalyticsClient,
                           events_repo: WhatsAppMessageEventsRepo):
    events_repo.create_event(
        message_log_id=log["Id"],
        whatsapp_message_id=log["WhatsAppMessageId"],
        event_type=event_type,
        event_data=str(payload)
    )

    base = {
        "id": str(log["Id"]),
        "userId": str(log["UserId"]),
        "batchId": str(log["BatchId"]) if log["BatchId"] else None,
        "messageId": log["WhatsAppMessageId"],
        "leadId": log["LeadId"],
        "recipientNumber": log["RecipientNumber"],
        "templateId": str(log["TemplateId"]),
        "sentAt": log["SentAt"].isoformat() if log["SentAt"] else None,
    }

    cosmos.merge_analytics_fields(
        doc_id=base["id"],
        user_id=base["userId"],
        **base
    )

@router.post("/message-events")
async def handle_all_events(request: Request):
    payload = await request.json()
    message_id = payload.get("messageId")
    if not message_id:
        raise HTTPException(status_code=400, detail="messageId is required.")

    logs_repo = WhatsAppSendLogsRepo()
    events_repo = WhatsAppMessageEventsRepo()
    cosmos = CosmosAnalyticsClient()
    templates_repo = WhatsAppTemplatesRepo()
    users_repo = UsersRepo()
    bot = BotmakerClient()

    log = logs_repo.get_by_message_id(message_id)
    if not log:
        raise HTTPException(status_code=404, detail="Message not found.")

    status_event = payload.get("status")
    generic_event = payload.get("event")

    if status_event:
        if status_event.lower() == "delivered":
            logs_repo.mark_delivered(message_id)
            if log["BatchId"]:
                cosmos.increment_campaign_counter(
                    batch_id=str(log["BatchId"]),
                    user_id=str(log["UserId"]),
                    template_id=str(log["TemplateId"]),
                    field="totalDelivered"
                )
            cosmos.merge_analytics_fields(
                doc_id=str(log["Id"]),
                user_id=str(log["UserId"]),
                deliveredAt=datetime.utcnow().isoformat()
            )
        elif status_event.lower() == "failed":
            logs_repo.mark_failed(message_id, reason=payload.get("reason"))
        _save_event_and_cosmos(payload, status_event, log, cosmos, events_repo)
        return {"status": "ok", "event": status_event}

    if generic_event == "read":
        logs_repo.mark_read(message_id)
        if log["BatchId"]:
            cosmos.increment_campaign_counter(
                batch_id=str(log["BatchId"]),
                user_id=str(log["UserId"]),
                template_id=str(log["TemplateId"]),
                field="totalRead"
            )
        read_at = datetime.utcnow()
        open_time = (read_at - log["SentAt"]).total_seconds() if log["SentAt"] else None
        cosmos.merge_analytics_fields(
            doc_id=str(log["Id"]),
            user_id=str(log["UserId"]),
            readAt=read_at.isoformat(),
            engagementMetrics={"openTime": open_time}
        )
        _save_event_and_cosmos(payload, "read", log, cosmos, events_repo)
        return {"status": "ok", "event": "read"}

    if generic_event == "click":
        template = templates_repo.get_by_id(log["TemplateId"])
        if not template:
            raise HTTPException(status_code=404, detail="Template not found for message.")

        original_tpl_key = (template["WhatsAppTemplateId"] or "").lower()
        advisor_tpl_map = {
            "cumpleanos_sami_skandia": "Asesor_Cumpleanos",
            "saludo_sami_skandia": "Asesor_Saludo",
            "vencimiento_sami_skandia": "Asesor_Vencimiento",
        }
        advisor_tpl_name = advisor_tpl_map.get(original_tpl_key)

        cliente_nombre_completo = log["RecipientName"] or ""
        cliente_primer_nombre = first_name(cliente_nombre_completo)
        cliente_numero = log["RecipientNumber"]

        advisor = users_repo.get_basic_info(log["UserId"])
        if not advisor:
            raise HTTPException(status_code=404, detail="Advisor user not found.")

        asesor_completo = advisor["Name"]
        url_telefono_fp = build_wa_me_link(advisor["CountryCodeWhatsApp"], advisor["WhatsAppNumber"])
        url_telefono_cliente = build_wa_me_link(57, cliente_numero)

        try:
            resp_client = await bot.send_template_by_name(
                to=cliente_numero,
                template_name="Cliente_Agradecimiento_Link",
                variables={
                    "nombre": cliente_primer_nombre,
                    "asesorCompleto": asesor_completo,
                    "urlTelefonoFp": url_telefono_fp
                }
            )
            logs_repo.create_log(
                batch_id=str(log["BatchId"]) if log["BatchId"] else None,
                user_id=str(log["UserId"]),
                lead_id=log["LeadId"],
                recipient_number=cliente_numero,
                recipient_name=cliente_nombre_completo,
                template_id=str(template["Id"]),
                message_content="Cliente_Agradecimiento_Link",
                message_id=resp_client.get("messageId") if isinstance(resp_client, dict) else None,
                status="SENT"
            )
        except Exception:
            pass

        if advisor_tpl_name:
            try:
                resp_advisor = await bot.send_template_by_name(
                    to=advisor["WhatsAppNumber"],
                    template_name=advisor_tpl_name,
                    variables={
                        "nombreCompleto": cliente_nombre_completo,
                        "urlTelefonoCliente": url_telefono_cliente
                    }
                )
                logs_repo.create_log(
                    batch_id=str(log["BatchId"]) if log["BatchId"] else None,
                    user_id=str(log["UserId"]),
                    lead_id=log["LeadId"],
                    recipient_number=advisor["WhatsAppNumber"],
                    recipient_name=asesor_completo,
                    template_id=str(template["Id"]),
                    message_content=advisor_tpl_name,
                    message_id=resp_advisor.get("messageId") if isinstance(resp_advisor, dict) else None,
                    status="SENT"
                )
            except Exception:
                pass

        clicked_at = datetime.utcnow()
        base_time = log["ReadAt"] or log["SentAt"]
        click_time = (clicked_at - base_time).total_seconds() if base_time else None

        user_agent = request.headers.get("User-Agent")
        ip = request.client.host if request.client else None

        cosmos.increment_campaign_counter(
            batch_id=str(log["BatchId"]) if log["BatchId"] else str(log["Id"]),
            user_id=str(log["UserId"]),
            template_id=str(log["TemplateId"]),
            field="totalClicked"
        )
        cosmos.merge_analytics_fields(
            doc_id=str(log["Id"]),
            user_id=str(log["UserId"]),
            clickedAt=clicked_at.isoformat(),
            userAgent=user_agent,
            engagementMetrics={"clickTime": click_time}
        )

        events_repo.create_event(
            message_log_id=log["Id"],
            whatsapp_message_id=log["WhatsAppMessageId"],
            event_type="click",
            event_data=str(payload | {"ip": ip, "userAgent": user_agent})
        )
        return {"status": "ok", "event": "click"}

    raise HTTPException(status_code=400, detail="Unknown event type.")
