from typing import Any

from pydantic import BaseModel, Field


class WhatsAppInboundRequest(BaseModel):
    phone_number: str = Field(min_length=8, max_length=32)
    message_text: str | None = None
    wa_message_id: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class WhatsAppInboundResponse(BaseModel):
    reply_text: str
    should_send: bool
    customer_status: str
