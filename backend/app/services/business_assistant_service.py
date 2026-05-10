import re
from dataclasses import dataclass
from decimal import Decimal

from app.calculators import calculate_margin


@dataclass(frozen=True)
class AssistantReply:
    reply_text: str
    handled: bool


@dataclass(frozen=True)
class MarginRequest:
    selling_price: Decimal
    hpp: Decimal


_MONEY_PATTERN = r"(?:rp\s*)?([0-9][0-9.,]*)(?:\s*(rb|ribu|k))?"


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


def _format_rupiah(value: Decimal) -> str:
    whole = int(value)
    return f"Rp{whole:,}".replace(",", ".")


def _format_percent(value: Decimal) -> str:
    return f"{value:.2f}".replace(".", ",")


def answer_active_message(message_text: str | None) -> AssistantReply:
    margin_request = parse_margin_request(message_text)
    text = _normalize_text(message_text)

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

    if any(keyword in text for keyword in ("margin", "hpp", "harga jual", "modal")):
        return AssistantReply(
            reply_text=(
                "Bisa Kak. Tulis harga jual dan HPP dalam satu pesan ya.\n\n"
                "Contoh: harga jual 18000 hpp 11500"
            ),
            handled=True,
        )

    return AssistantReply(
        reply_text=(
            "Untuk saat ini saya bisa bantu hitung margin dulu, Kak.\n\n"
            "Contoh: harga jual 18000 hpp 11500"
        ),
        handled=False,
    )
