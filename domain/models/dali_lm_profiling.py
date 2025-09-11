from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal, Any, Dict, List
from uuid import UUID

class DaliLMCheckClientRequest(BaseModel):
    email: Optional[EmailStr] = None
    identificationNumber: Optional[str] = None

class DaliLMStartProfilingRequest(BaseModel):
    clientEmail: Optional[EmailStr] = None
    clientIdentificationNumber: Optional[str] = None
    clientName: Optional[str] = None

class DaliLMSaveResponseRequest(BaseModel):
    profileId: UUID
    flowStep: Literal['initial_question', 'nightmare_flow', 'strategic_flow', 'followup', 'custom']
    questionId: str
    selectedAnswer: Optional[str] = None
    additionalNotes: Optional[str] = None

class DaliLMCompleteProfilingRequest(BaseModel):
    profileId: UUID
    finalData: Dict[str, Any]

class DaliLMProfilingResult(BaseModel):
    profileId: UUID
    finalProfileType: str
    riskLevel: str
    recommendedProducts: str
    investmentStrategy: str
    resultData: str # JSON string
    createdAt: str
