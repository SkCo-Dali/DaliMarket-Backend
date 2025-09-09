from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from auth_azure import get_current_user
from app.repositories.users_repo import UsersRepo
from app.repositories.whatsapp_sendlogs_repo import WhatsAppSendLogsRepo

router = APIRouter(prefix="/api/whatsapp", tags=["WhatsApp"])

@router.get("/limits/{userId}")
def get_limits(userId: UUID, current_user=Depends(get_current_user)):
    if str(userId) != current_user["sub"]:
        raise HTTPException(status_code=403, detail="No autorizado.")

    users_repo = UsersRepo()
    logs_repo = WhatsAppSendLogsRepo()

    limit = users_repo.get_daily_whatsapp_limit(userId)
    if limit is None:
        limit = 500  # default

    sent_today = logs_repo.count_sent_today(str(userId))
    remaining = max(0, limit - sent_today)

    # reset próximo a las 00:00 UTC (ajusta si quieres zona Colombia)
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    tomorrow_utc_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_to_reset = int((tomorrow_utc_midnight - now).total_seconds())

    return {
        "limit": limit,
        "sentToday": sent_today,
        "remaining": remaining,
        "resetInSeconds": seconds_to_reset
    }
