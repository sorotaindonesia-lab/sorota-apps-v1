from dataclasses import dataclass
from time import perf_counter
from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import AiUsageLog


@dataclass(frozen=True)
class AiCallResult:
    response: Any
    latency_ms: int


class OpenAIGateway:
    def __init__(self, client: OpenAI | None = None) -> None:
        client_kwargs: dict[str, str] = {}
        if settings.openai_api_key:
            client_kwargs["api_key"] = settings.openai_api_key
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url

        self.client = client or OpenAI(**client_kwargs)

    def responses_create(
        self,
        db: Session,
        *,
        task_type: str,
        customer_id: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> AiCallResult:
        selected_model = model or settings.openai_default_model
        started = perf_counter()
        response = self.client.responses.create(model=selected_model, **kwargs)
        latency_ms = int((perf_counter() - started) * 1000)

        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
        output_tokens = getattr(usage, "output_tokens", 0) if usage else 0
        cached_tokens = 0
        input_token_details = getattr(usage, "input_tokens_details", None) if usage else None
        if input_token_details:
            cached_tokens = getattr(input_token_details, "cached_tokens", 0) or 0

        db.add(
            AiUsageLog(
                customer_id=customer_id,
                task_type=task_type,
                model=selected_model,
                input_tokens=input_tokens or 0,
                output_tokens=output_tokens or 0,
                cached_tokens=cached_tokens,
                latency_ms=latency_ms,
                prompt_version=settings.openai_prompt_version,
            )
        )
        db.commit()

        return AiCallResult(response=response, latency_ms=latency_ms)
