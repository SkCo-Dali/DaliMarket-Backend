from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID

class DaliLMUserInput(BaseModel):
    name: str
    email: EmailStr
    role: str
    isActive: bool = True

    @field_validator("name")
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v

    @field_validator("email")
    def email_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("El correo no puede estar vacío")
        return v

    @field_validator("role")
    def role_must_be_valid(cls, v):
        allowed_roles = ['admin', 'seguridad', 'analista', 'supervisor', 'gestor', 'director', 'promotor', 'aliado', 'socio', 'fp']
        if v not in allowed_roles:
            raise ValueError(f"El rol '{v}' no es válido. Roles permitidos: {', '.join(allowed_roles)}")
        return v

class DaliLMUser(DaliLMUserInput):
    id: UUID
