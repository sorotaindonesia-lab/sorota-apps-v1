from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class EarlyWarningEventRead(BaseModel):
    id: UUID
    customer_id: UUID | None = None
    business_id: UUID | None = None
    rule_id: UUID | None = None
    severity: str
    title: str
    message: str
    evidence: dict[str, Any] | None = None
    status: str
    scheduled_send_at: datetime | None = None
    sent_at: datetime | None = None
    created_at: datetime


class EarlyWarningListResponse(BaseModel):
    items: list[EarlyWarningEventRead]
