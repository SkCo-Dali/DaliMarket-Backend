from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from uuid import UUID
from auth_azure import get_current_user
from app.models.whatsapp import SendMassRequest, SendMassResponse, BatchStatusResponse, SendLogsResponse, ValidateNumbersRequest, ValidateNumbersResponse, ValidateNumberResult
from app.db import obtener_userId, obtener_TemplateInfo
from app.repositories.whatsapp_batches_repo import WhatsAppBatchesRepo
from app.repositories.whatsapp_sendlogs_repo import WhatsAppSendLogsRepo
from app.repositories.whatsapp_idempotency_repo import WhatsAppIdempotencyRepo
from app.services.send_service import process_batch_async
from app.services.limit_service import WhatsAppLimitService

from app.utils.phone import is_valid_co_number

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

@router.post("/send-mass", response_model=SendMassResponse)
async def send_mass(
    request: SendMassRequest,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user)
):  
    # 1) Autorización básica
    UserId = await obtener_userId(current_user["email"])
    WhatsAppTemplateInfo = await obtener_TemplateInfo(request.templateId)
    if request.userId != UserId[0]:
        raise HTTPException(status_code=403, detail="Usuario no autorizado.")

    if not request.leads:
        raise HTTPException(status_code=400, detail="No hay leads para enviar.")

    # 2) Validar límite + reservar cupo con idempotencia

    limiter = WhatsAppLimitService()
    reservation = limiter.ensure_and_reserve(
        user_id=request.userId,
        messages_to_send=len(request.leads),
        idempotency_key=request.idempotencyKey
    )
    print(f"reservation: {reservation}")

    if reservation.get("already_done"):
        row = reservation["existing"]
        # row schema (desde WhatsAppIdempotencyRepo.get_by_key):
        # Id, UserId, IdempotencyKey, MessagesCount, BatchId, MessageId, Status, CreatedAt, ExpiresAt
        batch_id = row[4]
        if not batch_id:
            # Edge case: quedó COMPLETED pero sin batch_id (no debería suceder en /send-mass)
            raise HTTPException(status_code=409, detail="Solicitud idempotente ya procesada, pero no se encontró batch asociado.")
        return SendMassResponse(
            batchId=batch_id,
            status="PENDING",  # si quieres, consulta estado real abajo
            totalMessages=len(request.leads)
        )

    # 4) Crear el batch en SQL
    batches_repo = WhatsAppBatchesRepo()
    batch_id = batches_repo.create_batch(
        user_id=request.userId,
        template_id=request.templateId,
        total_messages=len(request.leads)
    )

    # 5) Lanzar el procesamiento asíncrono
    background_tasks.add_task(
        process_batch_async,
        batch_id=batch_id,
        user_id=request.userId,
        template_id=request.templateId,
        WhatsAppTemplateName=str(WhatsAppTemplateInfo[0]),
        ChannelId=str(WhatsAppTemplateInfo[1]),
        leads=request.leads,
        idempotency_key=request.idempotencyKey  # importante para cerrar la idempotencia al final
    )

    return SendMassResponse(
        batchId=batch_id,
        status="PENDING",
        totalMessages=len(request.leads)
    )

@router.get("/send-status/{batchId}", response_model=BatchStatusResponse)
def get_send_status(batchId: UUID, current_user=Depends(get_current_user)):
    repo = WhatsAppBatchesRepo()
    row = repo.get_batch_status(batchId)
    if not row:
        raise HTTPException(status_code=404, detail="Batch no encontrado.")

    # row: Id, Status, TotalMessages, SuccessfulMessages, FailedMessages, CreatedAt, CompletedAt
    return BatchStatusResponse(
        batchId=row[0],
        status=row[1],
        totalMessages=row[2],
        successfulMessages=row[3] or 0,
        failedMessages=row[4] or 0,
        createdAt=row[5],
        completedAt=row[6]
    )

@router.get("/send-logs/{userId}", response_model=SendLogsResponse)
def get_send_logs(userId: str, limit: int = 50, offset: int = 0, current_user=Depends(get_current_user)):
    if userId != current_user["sub"]:
        raise HTTPException(status_code=403, detail="No autorizado.")
    repo = WhatsAppSendLogsRepo()
    rows, total = repo.list_by_user(userId, limit, offset)
    items = []
    for r in rows:
        items.append({
            "id": r[0],
            "batchId": r[1],
            "userId": r[2],
            "leadId": r[3],
            "recipientNumber": r[4],
            "recipientName": r[5],
            "templateId": r[6],
            "messageContent": r[7],
            "whatsAppMessageId": r[8],
            "status": r[9],
            "sentAt": r[10],
            "deliveredAt": r[11],
            "readAt": r[12],
            "failureReason": r[13]
        })
    return SendLogsResponse(items=items, total=total)

@router.post("/validate-numbers", response_model=ValidateNumbersResponse)
def validate_numbers(req: ValidateNumbersRequest, current_user=Depends(get_current_user)):
    results = []
    for n in req.numbers:
        valid, reason = is_valid_co_number(n)
        results.append(ValidateNumberResult(number=n, isValid=valid, reason=reason))
    return ValidateNumbersResponse(results=results)
