from pydantic import BaseModel
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

# -------- Send mass --------
class LeadMessage(BaseModel):
    leadId: str
    name: Optional[str] = None
    contactId: str
    variables: Dict[str, str]

class SendMassRequest(BaseModel):
    userId: str
    templateId: UUID
    idempotencyKey: Optional[str] = None
    leads: List[LeadMessage]

class SendMassResponse(BaseModel):
    batchId: UUID
    status: str
    totalMessages: int

# -------- Batch status --------
class BatchStatusResponse(BaseModel):
    batchId: UUID
    status: str
    totalMessages: int
    successfulMessages: int
    failedMessages: int
    createdAt: datetime
    completedAt: Optional[datetime] = None

# -------- Logs --------
class SendLogItem(BaseModel):
    id: UUID
    batchId: Optional[UUID]
    userId: str
    leadId: str
    recipientNumber: str
    recipientName: Optional[str]
    templateId: UUID
    messageContent: str
    whatsAppMessageId: Optional[str]
    status: str
    sentAt: datetime
    deliveredAt: Optional[datetime]
    readAt: Optional[datetime]
    failureReason: Optional[str]

class SendLogsResponse(BaseModel):
    items: List[SendLogItem]
    total: int

# -------- Validate numbers --------
class ValidateNumbersRequest(BaseModel):
    numbers: List[str]

class ValidateNumberResult(BaseModel):
    number: str
    isValid: bool
    reason: Optional[str] = None

class ValidateNumbersResponse(BaseModel):
    results: List[ValidateNumberResult]
