import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.ai.answer_composer import AnswerComposerInput, compose_answer, compose_fallback_answer
from app.ai.database_mapper import DatabaseMappingResult, map_and_persist_message
from app.calculators import calculate_margin, recommend_price
from app.models import Business, Customer


@dataclass(frozen=True)
class AssistantReply:
    reply_text: str
    handled: bool
    data_mapping: dict[str, Any] | None = None


@dataclass(frozen=True)
class MarginRequest:
    selling_price: Decimal
    hpp: Decimal


@dataclass(frozen=True)
class RecommendPriceRequest:
    hpp: Decimal
    target_margin_percent: Decimal


_MONEY_PATTERN = r"(?:rp\s*)?([0-9][0-9.,]*)(?:\s*(rb|ribu|k))?"
_PERCENT_PATTERN = r"([0-9][0-9.,]*)\s*%?"


def _normalize_text(value: str | None) -> str:
    return (value or "").strip().lower()


def _parse_money(value: str, suffix: str | None = None) -> Decimal:
    cleaned = value.strip().strip(".,").replace(" ", "")
    suffix = (suffix or "").strip().lower()

    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "." in cleaned:
        parts = cleaned.split(".")
        cleaned = "".join(parts) if all(len(part) == 3 for part in parts[1:]) else cleaned
    elif "," in cleaned:
        parts = cleaned.split(",")
        cleaned = "".join(parts) if all(len(part) == 3 for part in parts[1:]) else cleaned.replace(",", ".")

    amount = Decimal(cleaned)
    if suffix in {"rb", "ribu", "k"}:
        amount *= Decimal("1000")

    return amount


def _extract_labeled_amount(text: str, labels: list[str]) -> Decimal | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:\b(?:{label_pattern})(?:nya)?\b)\s*(?:=|:|adalah|sekitar|kira-kira|kurang lebih)?\s*{_MONEY_PATTERN}"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None

    return _parse_money(match.group(1), match.group(2))


def _parse_percent(value: str) -> Decimal:
    return Decimal(value.strip().replace(",", "."))


def _extract_labeled_percent(text: str, labels: list[str]) -> Decimal | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:\b(?:{label_pattern})\b)\s*(?:=|:|nya|adalah)?\s*{_PERCENT_PATTERN}"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None

    return _parse_percent(match.group(1))


def parse_margin_request(message_text: str | None) -> MarginRequest | None:
    text = _normalize_text(message_text)
    if not text:
        return None

    selling_price = _extract_labeled_amount(text, ["harga jual", "jual", "harga"])
    hpp = _extract_labeled_amount(text, ["hpp", "modal", "harga pokok"])

    if selling_price is None or hpp is None:
        if "margin" not in text:
            return None

        numbers = re.findall(_MONEY_PATTERN, text, flags=re.IGNORECASE)
        if len(numbers) >= 2:
            selling_price = selling_price or _parse_money(numbers[0][0], numbers[0][1])
            hpp = hpp or _parse_money(numbers[1][0], numbers[1][1])

    if selling_price is None or hpp is None:
        return None

    return MarginRequest(selling_price=selling_price, hpp=hpp)


def parse_recommend_price_request(message_text: str | None) -> RecommendPriceRequest | None:
    text = _normalize_text(message_text)
    if not text:
        return None

    has_price_recommendation_intent = any(
        keyword in text
        for keyword in (
            "harga jual berapa",
            "harga berapa",
            "rekomendasi harga",
            "saran harga",
            "jual berapa",
            "pasang harga",
            "harga minimal",
        )
    )
    has_target_margin = "target margin" in text or "margin target" in text
    if not has_price_recommendation_intent and not has_target_margin:
        return None

    hpp = _extract_labeled_amount(text, ["hpp", "modal", "harga pokok"])
    target_margin = _extract_labeled_percent(text, ["target margin", "margin target", "margin"])

    if hpp is None or target_margin is None:
        return None

    return RecommendPriceRequest(hpp=hpp, target_margin_percent=target_margin)


def detect_general_intent(message_text: str | None) -> str:
    text = _normalize_text(message_text)
    if any(keyword in text for keyword in ("stok", "restock", "persediaan")):
        return "restock_advice"
    if any(keyword in text for keyword in ("supplier", "vendor", "bahan baku")):
        return "supplier_search"
    if any(keyword in text for keyword in ("promo", "diskon", "bundling", "paket")):
        return "promotion_advice"
    return "general_business_advice"


def _primary_business(customer: Customer | None) -> Business | None:
    if customer is None or not customer.businesses:
        return None
    return customer.businesses[0]


def _customer_context(customer: Customer | None) -> dict[str, object]:
    if customer is None:
        return {}
    return {
        "id": customer.id,
        "name": customer.name,
        "channel_key": customer.phone_number,
        "status": customer.status,
    }


def _business_context(customer: Customer | None) -> dict[str, object] | None:
    business = _primary_business(customer)
    if business is None:
        return None
    return {
        "id": business.id,
        "business_name": business.business_name,
        "business_category": business.business_category,
        "location": business.location,
        "known_products": [product.name for product in business.products],
    }


def _conversation_state(customer: Customer | None) -> str:
    return customer.conversation_state if customer else "ACTIVE"


def _compose(
    db: Session | None,
    payload: AnswerComposerInput,
    customer: Customer | None,
) -> str:
    if db is None:
        return compose_fallback_answer(payload)
    return compose_answer(db, payload, customer_id=customer.id if customer else None)


def _extract_mapping(
    db: Session | None,
    customer: Customer | None,
    message_text: str | None,
) -> DatabaseMappingResult | None:
    if db is None or customer is None:
        return None
    return map_and_persist_message(db, customer, message_text)


def _mapping_tool_result(mapping: DatabaseMappingResult | None) -> dict[str, Any]:
    if mapping is None:
        return {}
    return {"database_mapping": mapping.to_jsonable()}


def answer_active_message(
    message_text: str | None,
    *,
    db: Session | None = None,
    customer: Customer | None = None,
) -> AssistantReply:
    text = _normalize_text(message_text)
    data_mapping = _extract_mapping(db, customer, message_text)
    mapping_tool_result = _mapping_tool_result(data_mapping)
    recommend_request = parse_recommend_price_request(message_text)
    margin_request = parse_margin_request(message_text)

    if recommend_request:
        result = recommend_price(recommend_request.hpp, recommend_request.target_margin_percent)
        lower_bound, upper_bound = result["recommended_price_range"]
        tool_results = {
            "recommend_price": {
                "hpp": recommend_request.hpp,
                "target_margin_percent": recommend_request.target_margin_percent,
                "minimum_price": result["minimum_price"],
                "recommended_price_range": [lower_bound, upper_bound],
                "explanation": result["explanation"],
            }
        }
        tool_results.update(mapping_tool_result)
        payload = AnswerComposerInput(
            user_message=message_text or "",
            intent="pricing_advice",
            customer=_customer_context(customer),
            business=_business_context(customer),
            conversation_state=_conversation_state(customer),
            tool_results=tool_results,
        )
        reply = _compose(db, payload, customer)
        return AssistantReply(
            reply_text=reply,
            handled=True,
            data_mapping=data_mapping.to_jsonable() if data_mapping else None,
        )

    if margin_request:
        result = calculate_margin(margin_request.selling_price, margin_request.hpp)
        tool_results = {
            "margin_calculation": {
                "selling_price": margin_request.selling_price,
                "hpp": margin_request.hpp,
                "margin_amount": result["margin_amount"],
                "margin_percent": result["margin_percent"],
                "status": result["status"],
                "recommendation": result["recommendation"],
            }
        }
        tool_results.update(mapping_tool_result)
        payload = AnswerComposerInput(
            user_message=message_text or "",
            intent="margin_calculation",
            customer=_customer_context(customer),
            business=_business_context(customer),
            conversation_state=_conversation_state(customer),
            tool_results=tool_results,
        )
        reply = _compose(db, payload, customer)
        return AssistantReply(
            reply_text=reply,
            handled=True,
            data_mapping=data_mapping.to_jsonable() if data_mapping else None,
        )

    if any(keyword in text for keyword in ("target margin", "harga jual berapa", "rekomendasi harga", "saran harga")):
        return AssistantReply(
            reply_text=(
                "Bisa Kak. Tulis HPP dan target margin dalam satu pesan ya.\n\n"
                "Contoh: hpp 11500 target margin 30 harga jual berapa?"
            ),
            handled=True,
            data_mapping=data_mapping.to_jsonable() if data_mapping else None,
        )

    if any(keyword in text for keyword in ("margin", "hpp", "harga jual", "modal")):
        return AssistantReply(
            reply_text=(
                "Bisa Kak. Untuk hitung margin, tulis harga jual dan HPP.\n"
                "Contoh: harga jual 18000 hpp 11500\n\n"
                "Untuk rekomendasi harga jual, tulis HPP dan target margin.\n"
                "Contoh: hpp 11500 target margin 30 harga jual berapa?"
            ),
            handled=True,
            data_mapping=data_mapping.to_jsonable() if data_mapping else None,
        )

    intent = "business_profile_update" if data_mapping and data_mapping.has_updates else detect_general_intent(message_text)
    payload = AnswerComposerInput(
        user_message=message_text or "",
        intent=intent,
        customer=_customer_context(customer),
        business=_business_context(customer),
        conversation_state=_conversation_state(customer),
        tool_results=mapping_tool_result,
    )
    reply = _compose(db, payload, customer)
    return AssistantReply(
        reply_text=reply,
        handled=False,
        data_mapping=data_mapping.to_jsonable() if data_mapping else None,
    )
