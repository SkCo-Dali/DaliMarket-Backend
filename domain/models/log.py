# domain/models/log.py
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class Log(BaseModel):
    id: str = Field(..., description="Identificador único del log")
    user_id: str = Field(..., description="ID del usuario que realiza la acción")
    user_email: str = Field(..., description="Correo electrónico del usuario")
    opportunity_id: int = Field(..., description="ID de la oportunidad procesada")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Marca de tiempo del evento")

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()}
    )
