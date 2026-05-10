from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
import json
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.gateway import OpenAIGateway
from app.core.config import settings


@dataclass(frozen=True)
class AnswerComposerInput:
    user_message: str
    intent: str
    customer: dict[str, Any]
    business: dict[str, Any] | None
    conversation_state: str
    tool_results: dict[str, Any] = field(default_factory=dict)
    memories: list[dict[str, Any]] = field(default_factory=list)
    knowledge: list[dict[str, Any]] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)

    def to_jsonable(self) -> dict[str, Any]:
        return _to_jsonable(
            {
                "user_message": self.user_message,
                "intent": self.intent,
                "customer": self.customer,
                "business": self.business,
                "conversation_state": self.conversation_state,
                "tool_results": self.tool_results,
                "memories": self.memories,
                "knowledge": self.knowledge,
                "missing_fields": self.missing_fields,
            }
        )


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _prompt_text() -> str:
    prompt_path = Path(__file__).resolve().parent / "prompts" / "answer_composer.md"
    return prompt_path.read_text(encoding="utf-8")


def _business_name(payload: AnswerComposerInput) -> str | None:
    if not payload.business:
        return None
    value = payload.business.get("business_name")
    return str(value) if value else None


def _category_label(payload: AnswerComposerInput) -> str | None:
    if not payload.business:
        return None
    value = payload.business.get("business_category")
    if not value:
        return None
    return str(value).replace("_", " ")


def _format_rupiah(value: Any) -> str:
    amount = Decimal(str(value))
    return f"Rp{int(amount):,}".replace(",", ".")


def _format_percent(value: Any) -> str:
    return f"{Decimal(str(value)):.2f}".replace(".", ",")


def _fallback_margin_answer(payload: AnswerComposerInput) -> str:
    tool = payload.tool_results["margin_calculation"]
    business_name = _business_name(payload)
    category = _category_label(payload)

    opener = "Masih lumayan aman, Kak."
    if tool.get("status") == "thin":
        opener = "Marginnya mulai tipis, Kak."
    if business_name:
        opener = f"Untuk {business_name}, {opener[0].lower()}{opener[1:]}"

    context_hint = ""
    if category:
        context_hint = f" Karena bisnis Kakak masuk kategori {category}, jangan lupa cek biaya kecil seperti kemasan, promo, atau komisi platform kalau ada."

    return (
        f"{opener} Dengan HPP {_format_rupiah(tool['hpp'])} dan harga jual {_format_rupiah(tool['selling_price'])}, "
        f"margin kotornya {_format_rupiah(tool['margin_amount'])} atau sekitar {_format_percent(tool['margin_percent'])}%.\n\n"
        f"{tool['recommendation']}{context_hint}"
    )


def _fallback_recommend_price_answer(payload: AnswerComposerInput) -> str:
    tool = payload.tool_results["recommend_price"]
    lower_bound, upper_bound = tool["recommended_price_range"]
    business_name = _business_name(payload)

    opener = "Bisa, Kak."
    if business_name:
        opener = f"Bisa, Kak. Untuk {business_name},"

    return (
        f"{opener} kalau HPP-nya {_format_rupiah(tool['hpp'])} dan target margin {_format_percent(tool['target_margin_percent'])}%, "
        f"harga minimalnya sekitar {_format_rupiah(tool['minimum_price'])}.\n\n"
        f"Supaya lebih aman dan gampang dites ke pembeli, range jualnya bisa di {_format_rupiah(lower_bound)}-"
        f"{_format_rupiah(upper_bound)}. Mulai tes dari tengah range dulu, lalu lihat respons pembeli."
    )


def compose_fallback_answer(payload: AnswerComposerInput) -> str:
    if payload.missing_fields:
        if "hpp" in payload.missing_fields and "selling_price" in payload.missing_fields:
            return "Bisa saya bantu hitung, Kak. Kirim harga jual dan HPP dalam satu pesan ya. Contoh: harga jual 18000 hpp 11500."
        if "hpp" in payload.missing_fields:
            return "Bisa Kak. HPP-nya berapa? Contoh: hpp 11500 target margin 30 harga jual berapa?"
        if "target_margin_percent" in payload.missing_fields:
            return "Bisa Kak. Target margin yang Kakak mau berapa persen? Contoh: hpp 11500 target margin 30 harga jual berapa?"

    if "margin_calculation" in payload.tool_results:
        return _fallback_margin_answer(payload)

    if "recommend_price" in payload.tool_results:
        return _fallback_recommend_price_answer(payload)

    return (
        "Saya bisa bantu dari hitungan bisnis yang paling praktis dulu, Kak. "
        "Coba kirim harga jual dan HPP untuk cek margin, atau HPP dan target margin untuk rekomendasi harga jual."
    )


def _extract_response_text(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return str(output_text).strip()

    output = getattr(response, "output", None)
    if not output:
        return ""

    parts: list[str] = []
    for item in output:
        for content in getattr(item, "content", []) or []:
            text = getattr(content, "text", None)
            if text:
                parts.append(str(text))
    return "\n".join(parts).strip()


def compose_answer(
    db: Session,
    payload: AnswerComposerInput,
    *,
    customer_id: UUID | None = None,
    gateway: OpenAIGateway | None = None,
) -> str:
    if not settings.openai_api_key:
        return compose_fallback_answer(payload)

    try:
        result = (gateway or OpenAIGateway()).responses_create(
            db,
            task_type="answer_composer",
            customer_id=customer_id,
            input=[
                {"role": "system", "content": _prompt_text()},
                {
                    "role": "user",
                    "content": json.dumps(payload.to_jsonable(), ensure_ascii=False),
                },
            ],
        )
        answer = _extract_response_text(result.response)
    except Exception:
        return compose_fallback_answer(payload)

    return answer or compose_fallback_answer(payload)
