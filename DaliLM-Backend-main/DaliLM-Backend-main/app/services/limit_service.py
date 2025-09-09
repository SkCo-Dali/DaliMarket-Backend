# app/services/limit_service.py
from fastapi import HTTPException, status
from uuid import UUID
from app.repositories.users_repo import UsersRepo
from app.repositories.whatsapp_sendlogs_repo import WhatsAppSendLogsRepo
from app.repositories.whatsapp_idempotency_repo import WhatsAppIdempotencyRepo

DEFAULT_DAILY_WHATSAPP_LIMIT = 500

class WhatsAppLimitService:
    def __init__(self,
                 users_repo: UsersRepo = None,
                 logs_repo: WhatsAppSendLogsRepo = None,
                 idemp_repo: WhatsAppIdempotencyRepo = None):
        self.users_repo = users_repo or UsersRepo()
        self.logs_repo = logs_repo or WhatsAppSendLogsRepo()
        self.idemp_repo = idemp_repo or WhatsAppIdempotencyRepo()

    def ensure_and_reserve(self, user_id: UUID, messages_to_send: int, idempotency_key: str | None):
        """
        - Si hay idempotencyKey y ya existe COMPLETED → no volver a contar ni enviar (devuelve metadata).
        - Si hay idempotencyKey y está PENDING o no existe → valida cupo y crea registro PENDING (reserva).
        - Si no hay idempotencyKey → valida cupo (no hay reserva explícita).
        """
        existing = None
        if idempotency_key:
            existing = self.idemp_repo.get_by_key(idempotency_key)
            if existing:
                status_val = existing[6]
                if status_val == "COMPLETED":
                    # Ya se hizo. Informar al caller para que retorne el resultado previo sin repetir envío ni cupo.
                    return {"already_done": True, "existing": existing}
                # Si está PENDING, no contamos de nuevo; asumimos que es el mismo intento en progreso.
                # Dependiendo de tu diseño, podrías bloquear aquí. Lo dejamos pasar.

        # Límite configurado
        limit = self.users_repo.get_daily_whatsapp_limit(user_id)
        limit = limit if limit is not None else DEFAULT_DAILY_WHATSAPP_LIMIT
        sent_today = self.logs_repo.count_sent_today(str(user_id))
        remaining = limit - sent_today

        if remaining <= 0 or remaining < messages_to_send:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "daily_limit_exceeded",
                    "message": f"Intentas enviar {messages_to_send}, disponible {max(0, remaining)}.",
                    "limit": limit,
                    "sentToday": sent_today,
                    "remaining": max(0, remaining)
                }
            )

        # Reserva
        if idempotency_key and not existing:
            self.idemp_repo.create_pending(str(user_id), idempotency_key, messages_to_send)

        return {
            "already_done": False,
            "limit": limit,
            "sentToday": sent_today,
            "remaining": remaining
        }
