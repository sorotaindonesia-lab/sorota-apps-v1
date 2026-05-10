from typing import Any

from pydantic import BaseModel, Field


class TelegramInboundRequest(BaseModel):
    telegram_user_id: str | None = None
    chat_id: str = Field(min_length=1, max_length=64)
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    message_text: str | None = None
    telegram_message_id: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class TelegramInboundResponse(BaseModel):
    reply_text: str
    should_send: bool
    customer_status: str
