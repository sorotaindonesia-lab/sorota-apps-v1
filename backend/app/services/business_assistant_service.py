import re
from dataclasses import dataclass
from decimal import Decimal

from app.calculators import calculate_margin, recommend_price


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


def _format_rupiah(value: Decimal) -> str:
    whole = int(value)
    return f"Rp{whole:,}".replace(",", ".")


def _format_percent(value: Decimal) -> str:
    return f"{value:.2f}".replace(".", ",")


def answer_active_message(message_text: str | None) -> AssistantReply:
    recommend_request = parse_recommend_price_request(message_text)
    margin_request = parse_margin_request(message_text)
    text = _normalize_text(message_text)

    if recommend_request:
        result = recommend_price(recommend_request.hpp, recommend_request.target_margin_percent)
        lower_bound, upper_bound = result["recommended_price_range"]
        midpoint = (lower_bound + upper_bound) / Decimal("2")
        reply = (
            "Rekomendasi harga jual Kakak:\n\n"
            f"HPP: {_format_rupiah(recommend_request.hpp)}\n"
            f"Target margin: {_format_percent(recommend_request.target_margin_percent)}%\n"
            f"Harga minimal: {_format_rupiah(result['minimum_price'])}\n"
            f"Range aman: {_format_rupiah(lower_bound)}-{_format_rupiah(upper_bound)}\n\n"
            f"Saran saya mulai tes di {_format_rupiah(midpoint)} dulu, lalu lihat respons pembeli."
        )
        return AssistantReply(reply_text=reply, handled=True)

    if margin_request:
        result = calculate_margin(margin_request.selling_price, margin_request.hpp)
        reply = (
            "Margin produk Kakak:\n\n"
            f"Harga jual: {_format_rupiah(margin_request.selling_price)}\n"
            f"HPP: {_format_rupiah(margin_request.hpp)}\n"
            f"Margin: {_format_rupiah(result['margin_amount'])}\n"
            f"Margin %: {_format_percent(result['margin_percent'])}%\n\n"
            f"{result['recommendation']}"
        )
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

    return AssistantReply(
        reply_text=(
            "Untuk saat ini saya bisa bantu hitung margin dan rekomendasi harga jual dulu, Kak.\n\n"
            "Contoh hitung margin: harga jual 18000 hpp 11500\n"
            "Contoh rekomendasi harga: hpp 11500 target margin 30 harga jual berapa?"
        ),
        handled=False,
    )
