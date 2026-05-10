from typing import Any

from pydantic import BaseModel, Field


class AdminCommandRequest(BaseModel):
    command: str = Field(min_length=1)


class AdminCommandResponse(BaseModel):
    intent: str
    summary: str
    data: list[dict[str, Any]]
    suggested_actions: list[str]
