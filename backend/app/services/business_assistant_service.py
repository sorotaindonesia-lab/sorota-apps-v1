import re
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.ai.answer_composer import AnswerComposerInput, compose_answer, compose_fallback_answer
from app.calculators import calculate_margin, recommend_price
from app.models import Business, Customer


@dataclass(frozen=True)
class AssistantReply:
    reply_text: str
    handled: bool


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
    cleaned = value.strip().replace(" ", "")
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
    pattern = rf"(?:\b(?:{label_pattern})\b)\s*(?:=|:|nya|adalah)?\s*{_MONEY_PATTERN}"
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


def answer_active_message(
    message_text: str | None,
    *,
    db: Session | None = None,
    customer: Customer | None = None,
) -> AssistantReply:
    recommend_request = parse_recommend_price_request(message_text)
    margin_request = parse_margin_request(message_text)
    text = _normalize_text(message_text)

    if recommend_request:
        result = recommend_price(recommend_request.hpp, recommend_request.target_margin_percent)
        lower_bound, upper_bound = result["recommended_price_range"]
        payload = AnswerComposerInput(
            user_message=message_text or "",
            intent="pricing_advice",
            customer=_customer_context(customer),
            business=_business_context(customer),
            conversation_state=_conversation_state(customer),
            tool_results={
                "recommend_price": {
                    "hpp": recommend_request.hpp,
                    "target_margin_percent": recommend_request.target_margin_percent,
                    "minimum_price": result["minimum_price"],
                    "recommended_price_range": [lower_bound, upper_bound],
                    "explanation": result["explanation"],
                }
            },
        )
        reply = _compose(db, payload, customer)
        return AssistantReply(reply_text=reply, handled=True)

    if margin_request:
        result = calculate_margin(margin_request.selling_price, margin_request.hpp)
        payload = AnswerComposerInput(
            user_message=message_text or "",
            intent="margin_calculation",
            customer=_customer_context(customer),
            business=_business_context(customer),
            conversation_state=_conversation_state(customer),
            tool_results={
                "margin_calculation": {
                    "selling_price": margin_request.selling_price,
                    "hpp": margin_request.hpp,
                    "margin_amount": result["margin_amount"],
                    "margin_percent": result["margin_percent"],
                    "status": result["status"],
                    "recommendation": result["recommendation"],
                }
            },
        )
        reply = _compose(db, payload, customer)
        return AssistantReply(reply_text=reply, handled=True)

    if any(keyword in text for keyword in ("target margin", "harga jual berapa", "rekomendasi harga", "saran harga")):
        return AssistantReply(
            reply_text=(
                "Bisa Kak. Tulis HPP dan target margin dalam satu pesan ya.\n\n"
                "Contoh: hpp 11500 target margin 30 harga jual berapa?"
            ),
            handled=True,
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
        )

    payload = AnswerComposerInput(
        user_message=message_text or "",
        intent=detect_general_intent(message_text),
        customer=_customer_context(customer),
        business=_business_context(customer),
        conversation_state=_conversation_state(customer),
        tool_results={},
    )
    reply = _compose(db, payload, customer)
    return AssistantReply(
        reply_text=reply,
        handled=False,
    )
