from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gateway import OpenAIGateway
from app.core.config import settings
from app.models import Business, Customer, Product, UserMemory


_MONEY_PATTERN = r"(?:rp\s*)?([0-9][0-9.,]*)(?:\s*(rb|ribu|k))?"
_BUSINESS_CATEGORIES = {
    "kuliner",
    "retail",
    "fashion",
    "laundry",
    "warung",
    "toko_kelontong",
    "coffee_shop",
    "reseller",
    "jasa",
    "lainnya",
}
_BUSINESS_FIELDS = {
    "business_name",
    "business_category",
    "business_subcategory",
    "location",
    "business_stage",
    "target_margin_percent",
    "notes",
}


@dataclass(frozen=True)
class ExtractedProduct:
    name: str
    category: str | None = None
    selling_price: Decimal | None = None
    hpp: Decimal | None = None
    margin_percent: Decimal | None = None
    confidence: Decimal = Decimal("0.75")

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "selling_price": _json_decimal(self.selling_price),
            "hpp": _json_decimal(self.hpp),
            "margin_percent": _json_decimal(self.margin_percent),
            "confidence": _json_decimal(self.confidence),
        }


@dataclass(frozen=True)
class ExtractedMemory:
    key: str
    value: Any
    confidence: Decimal = Decimal("0.75")

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": _to_jsonable(self.value),
            "confidence": _json_decimal(self.confidence),
        }


@dataclass(frozen=True)
class DatabaseMappingResult:
    business: dict[str, Any] = field(default_factory=dict)
    products: list[ExtractedProduct] = field(default_factory=list)
    memories: list[ExtractedMemory] = field(default_factory=list)
    ignored: list[str] = field(default_factory=list)
    source: str = "fallback"

    @property
    def has_updates(self) -> bool:
        return bool(self.business or self.products or self.memories)

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "business": _to_jsonable(self.business),
            "products": [product.to_jsonable() for product in self.products],
            "memories": [memory.to_jsonable() for memory in self.memories],
            "ignored": self.ignored,
            "source": self.source,
            "has_updates": self.has_updates,
        }


def _json_decimal(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def _prompt_text() -> str:
    prompt_path = Path(__file__).resolve().parent / "prompts" / "memory_extractor.md"
    return prompt_path.read_text(encoding="utf-8")


def _clean_text(value: str | None) -> str:
    return (value or "").strip()


def _normalize_text(value: str | None) -> str:
    return _clean_text(value).lower()


def _parse_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        return None


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


def _extract_labeled_money(text: str, labels: list[str]) -> Decimal | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:\b(?:{label_pattern})(?:nya)?\b)\s*(?:=|:|adalah|sekitar|kira-kira|kurang lebih)?\s*{_MONEY_PATTERN}"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return _parse_money(match.group(1), match.group(2))


def _extract_location(message_text: str) -> str | None:
    pattern = (
        r"(?:\bdi|lokasi(?:nya)?(?:\s+di)?|area|daerah)\s+"
        r"([A-Za-zÀ-ÖØ-öø-ÿ\s.-]+?)"
        r"(?=,|\.|\s+(?:harga|hpp|modal|jual|dengan|dan|sekitar|saya|aku)\b|$)"
    )
    match = re.search(pattern, message_text, flags=re.IGNORECASE)
    if not match:
        return None

    location = re.sub(r"\s+", " ", match.group(1)).strip(" .,-")
    if not location:
        return None

    return location.title() if location.islower() else location


def _detect_category(text: str) -> str | None:
    if any(keyword in text for keyword in ("ayam", "geprek", "nasi", "bakso", "mie", "makanan", "minuman", "kuliner")):
        return "kuliner"
    if any(keyword in text for keyword in ("kopi", "coffee", "cafe", "kafe")):
        return "coffee_shop"
    if "laundry" in text:
        return "laundry"
    if any(keyword in text for keyword in ("baju", "fashion", "sepatu", "hijab", "kaos")):
        return "fashion"
    if any(keyword in text for keyword in ("kelontong", "sembako")):
        return "toko_kelontong"
    if "warung" in text:
        return "warung"
    if "reseller" in text:
        return "reseller"
    if "jasa" in text:
        return "jasa"
    if "retail" in text:
        return "retail"
    return None


def _trim_product_phrase(value: str) -> str:
    product = re.sub(r"\s+", " ", value).strip(" .,-")
    product = re.sub(r"^(produk|menu|barang)\s+(utama\s+)?", "", product, flags=re.IGNORECASE).strip()
    product = re.sub(r"\s+(harga|hpp|modal).*$", "", product, flags=re.IGNORECASE).strip(" .,-")
    return product.lower()


def _looks_like_product_name(value: str) -> bool:
    if not value or value in {"saya", "aku", "kami", "bisnis", "usaha"}:
        return False
    if value.startswith(("saya ", "aku ", "kami ")):
        return False
    if any(keyword in value for keyword in (" sepi", " turun", " rame", "ramai", "laris")):
        return False
    return True


def _extract_product_name(message_text: str, known_products: list[str]) -> str | None:
    text = _normalize_text(message_text)
    for product in sorted(known_products, key=len, reverse=True):
        if product and product.lower() in text:
            return product

    patterns = [
        r"\b(?:saya|aku|kami)\s+jual\s+(.+?)(?=\s+di\b|,|\.|\s+(?:harga|hpp|modal|dengan|yang)\b|$)",
        r"\bjual(?:an)?\s+(?:produk|menu|barang)\s+(.+?)(?=\s+di\b|,|\.|\s+(?:harga|hpp|modal|dengan|yang)\b|$)",
        r"\bjualan\s+(.+?)(?=\s+di\b|,|\.|\s+(?:harga|hpp|modal|dengan|yang)\b|$)",
        r"\bproduk(?:\s+utama)?(?:nya)?\s+(.+?)(?=\s+di\b|,|\.|\s+(?:harga|hpp|modal|dengan|yang)\b|$)",
        r"\bmenu(?:\s+utama)?(?:nya)?\s+(.+?)(?=\s+di\b|,|\.|\s+(?:harga|hpp|modal|dengan|yang)\b|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message_text, flags=re.IGNORECASE)
        if not match:
            continue
        product = _trim_product_phrase(match.group(1))
        if _looks_like_product_name(product):
            return product

    if len(known_products) == 1 and (
        _extract_labeled_money(text, ["harga jual", "jual", "harga"]) is not None
        or _extract_labeled_money(text, ["hpp", "modal", "harga pokok"]) is not None
    ):
        return known_products[0]

    return None


def _calculate_margin_percent(selling_price: Decimal | None, hpp: Decimal | None) -> Decimal | None:
    if selling_price is None or hpp is None or selling_price == 0:
        return None
    return ((selling_price - hpp) / selling_price * Decimal("100")).quantize(Decimal("0.01"))


def _known_products(customer: Customer | None) -> list[str]:
    if customer is None or not customer.businesses:
        return []
    return [product.name for product in customer.businesses[0].products if product.name]


def _context_payload(customer: Customer | None) -> dict[str, Any]:
    if customer is None:
        return {}
    business = customer.businesses[0] if customer.businesses else None
    return {
        "customer": {
            "id": str(customer.id),
            "name": customer.name,
            "channel_key": customer.phone_number,
            "conversation_state": customer.conversation_state,
        },
        "business": (
            {
                "id": str(business.id),
                "business_name": business.business_name,
                "business_category": business.business_category,
                "business_subcategory": business.business_subcategory,
                "location": business.location,
                "business_stage": business.business_stage,
                "target_margin_percent": _json_decimal(business.target_margin_percent),
                "known_products": [
                    {
                        "name": product.name,
                        "category": product.category,
                        "selling_price": _json_decimal(product.selling_price),
                        "hpp": _json_decimal(product.hpp),
                        "margin_percent": _json_decimal(product.margin_percent),
                    }
                    for product in business.products
                ],
            }
            if business
            else None
        ),
    }


def _fallback_database_mapping(message_text: str | None, customer: Customer | None = None) -> DatabaseMappingResult:
    raw_text = _clean_text(message_text)
    text = _normalize_text(message_text)
    if not raw_text:
        return DatabaseMappingResult(ignored=["empty_message"])

    business: dict[str, Any] = {}
    ignored: list[str] = []

    category = _detect_category(text)
    if category:
        business["business_category"] = category

    location = _extract_location(raw_text)
    if location:
        business["location"] = location

    known_products = _known_products(customer)
    product_name = _extract_product_name(raw_text, known_products)
    selling_price = _extract_labeled_money(text, ["harga jual", "jual", "harga"])
    hpp = _extract_labeled_money(text, ["hpp", "modal", "harga pokok"])

    products: list[ExtractedProduct] = []
    memories: list[ExtractedMemory] = []
    if product_name:
        products.append(
            ExtractedProduct(
                name=product_name,
                category=category,
                selling_price=selling_price,
                hpp=hpp,
                margin_percent=_calculate_margin_percent(selling_price, hpp),
            )
        )
        memories.append(ExtractedMemory(key="main_product", value=product_name))
    elif selling_price is not None or hpp is not None:
        ignored.append("product_price_without_product_name")

    return DatabaseMappingResult(
        business=business,
        products=products,
        memories=memories,
        ignored=ignored,
        source="fallback",
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


def _parse_json_object(value: str) -> dict[str, Any]:
    cleaned = value.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("database mapping response must be a JSON object")
    return parsed


def _normalize_business(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}

    normalized: dict[str, Any] = {}
    for key, item in value.items():
        if key not in _BUSINESS_FIELDS or item in (None, ""):
            continue
        if key == "business_category":
            category = str(item).strip().lower().replace(" ", "_")
            if category not in _BUSINESS_CATEGORIES:
                continue
            normalized[key] = category
        elif key == "target_margin_percent":
            decimal_value = _parse_decimal(item)
            if decimal_value is not None:
                normalized[key] = decimal_value
        else:
            normalized[key] = str(item).strip()
    return normalized


def _normalize_products(value: Any) -> list[ExtractedProduct]:
    if not isinstance(value, list):
        return []

    products: list[ExtractedProduct] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or "").strip().lower()
        if not name:
            continue

        selling_price = _parse_decimal(item.get("selling_price"))
        hpp = _parse_decimal(item.get("hpp"))
        margin_percent = _parse_decimal(item.get("margin_percent")) or _calculate_margin_percent(selling_price, hpp)
        confidence = _parse_decimal(item.get("confidence")) or Decimal("0.75")

        products.append(
            ExtractedProduct(
                name=name,
                category=str(item["category"]).strip() if item.get("category") else None,
                selling_price=selling_price,
                hpp=hpp,
                margin_percent=margin_percent,
                confidence=confidence,
            )
        )
    return products


def _normalize_memories(value: Any) -> list[ExtractedMemory]:
    if not isinstance(value, list):
        return []

    memories: list[ExtractedMemory] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "").strip()
        if not key or item.get("value") in (None, ""):
            continue
        confidence = _parse_decimal(item.get("confidence")) or Decimal("0.75")
        memories.append(ExtractedMemory(key=key, value=item["value"], confidence=confidence))
    return memories


def _mapping_from_payload(payload: dict[str, Any], *, source: str) -> DatabaseMappingResult:
    ignored_raw = payload.get("ignored", [])
    ignored = [str(item) for item in ignored_raw] if isinstance(ignored_raw, list) else []
    return DatabaseMappingResult(
        business=_normalize_business(payload.get("business")),
        products=_normalize_products(payload.get("products")),
        memories=_normalize_memories(payload.get("memories")),
        ignored=ignored,
        source=source,
    )


def extract_database_mapping(
    message_text: str | None,
    *,
    db: Session | None = None,
    customer: Customer | None = None,
    gateway: OpenAIGateway | None = None,
) -> DatabaseMappingResult:
    if not settings.openai_api_key or db is None:
        return _fallback_database_mapping(message_text, customer)

    try:
        result = (gateway or OpenAIGateway()).responses_create(
            db,
            task_type="database_mapper",
            customer_id=customer.id if customer else None,
            input=[
                {"role": "system", "content": _prompt_text()},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "user_message": message_text or "",
                            "existing_context": _context_payload(customer),
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        )
        response_text = _extract_response_text(result.response)
        return _mapping_from_payload(_parse_json_object(response_text), source="llm")
    except Exception:
        return _fallback_database_mapping(message_text, customer)


def _get_or_create_business(db: Session, customer: Customer) -> Business:
    if customer.businesses:
        return customer.businesses[0]

    business = Business(customer_id=customer.id)
    customer.businesses.append(business)
    db.add(business)
    db.flush()
    return business


def _upsert_product(db: Session, business: Business, extracted: ExtractedProduct) -> None:
    existing_by_name = {product.name.lower(): product for product in business.products}
    product = existing_by_name.get(extracted.name.lower())
    if product is None:
        product = Product(business_id=business.id, name=extracted.name)
        business.products.append(product)
        db.add(product)

    if extracted.category:
        product.category = extracted.category
    if extracted.selling_price is not None:
        product.selling_price = extracted.selling_price
    if extracted.hpp is not None:
        product.hpp = extracted.hpp

    product.margin_percent = (
        extracted.margin_percent
        or _calculate_margin_percent(product.selling_price, product.hpp)
        or product.margin_percent
    )


def _memory_value(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {"value": value}


def _upsert_memory(db: Session, customer: Customer, extracted: ExtractedMemory) -> None:
    memory = db.scalar(
        select(UserMemory).where(
            UserMemory.customer_id == customer.id,
            UserMemory.memory_key == extracted.key,
        )
    )
    if memory is None:
        memory = UserMemory(customer_id=customer.id, memory_key=extracted.key)
        db.add(memory)

    memory.memory_value = _memory_value(extracted.value)
    memory.confidence = extracted.confidence
    memory.source = "chat_extractor"


def persist_database_mapping(db: Session, customer: Customer, mapping: DatabaseMappingResult) -> None:
    if not mapping.has_updates:
        return

    business: Business | None = None
    if mapping.business or mapping.products:
        business = _get_or_create_business(db, customer)

    if business is not None:
        for key, value in mapping.business.items():
            if key in _BUSINESS_FIELDS and value not in (None, ""):
                setattr(business, key, value)

        for product in mapping.products:
            _upsert_product(db, business, product)

    for memory in mapping.memories:
        _upsert_memory(db, customer, memory)

    db.flush()


def map_and_persist_message(
    db: Session,
    customer: Customer,
    message_text: str | None,
    *,
    gateway: OpenAIGateway | None = None,
) -> DatabaseMappingResult:
    mapping = extract_database_mapping(message_text, db=db, customer=customer, gateway=gateway)
    persist_database_mapping(db, customer, mapping)
    return mapping
