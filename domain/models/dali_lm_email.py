from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import List, Optional
from uuid import UUID

class DaliLMEmailMessage(BaseModel):
    to: EmailStr
    subject: str
    html_content: Optional[str] = None
    plain_content: Optional[str] = None
    LeadId: UUID
    Campaign: Optional[str] = None

    @field_validator("subject", mode="after")
    @classmethod
    def subject_not_empty(cls, v: str):
        if not v or not v.strip():
            raise ValueError("El asunto no puede estar vacío.")
        return v

    @model_validator(mode="after")
    def check_body(self):
        has_html = bool(self.html_content and self.html_content.strip())
        has_plain = bool(self.plain_content and self.plain_content.strip())
        if not (has_html or has_plain):
            raise ValueError("Debe enviar html_content o plain_content.")
        return self

class DaliLMEmailInput(BaseModel):
    recipients: List[DaliLMEmailMessage]

    @field_validator("recipients")
    def validate_recipients(cls, v):
        if not v:
            raise ValueError("Debe especificar al menos un destinatario.")
        return v
