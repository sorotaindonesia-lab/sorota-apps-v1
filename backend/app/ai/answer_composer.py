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


def _known_products(payload: AnswerComposerInput) -> list[str]:
    if not payload.business:
        return []
    products = payload.business.get("known_products") or []
    return [str(product) for product in products if product]


def _fallback_general_business_answer(payload: AnswerComposerInput) -> str:
    business_name = _business_name(payload)
    category = _category_label(payload)
    products = _known_products(payload)
    text = payload.user_message.lower()

    subject = "bisnis Kakak"
    if business_name:
        subject = business_name
    elif category:
        subject = f"bisnis {category} Kakak"

    product_hint = ""
    if products:
        product_hint = f" Fokus dulu ke produk yang sudah jelas, seperti {', '.join(products[:2])}."

    if any(keyword in text for keyword in ("sepi", "jualan turun", "omzet turun", "order turun", "penjualan turun")):
        return (
            f"Kalau {subject} sedang terasa sepi, jangan langsung banting harga dulu, Kak. Cek dulu sumber masalahnya: "
            f"apakah traffic turun, orang tanya tapi tidak beli, atau pembeli lama belum repeat order.{product_hint}\n\n"
            "Langkah praktis hari ini: catat 3 produk yang paling sering ditanya, buat promo kecil untuk salah satunya, "
            "lalu follow up pelanggan lama dengan penawaran yang jelas. Kalau mau, kirim omzet atau jumlah order 7 hari terakhir, nanti saya bantu baca polanya."
        )

    if any(keyword in text for keyword in ("promo", "diskon", "bundling", "paket")):
        return (
            f"Untuk {subject}, promo paling aman biasanya bukan sekadar diskon besar, Kak. Lebih baik bikin paket yang tetap menjaga margin."
            f"{product_hint}\n\n"
            "Coba mulai dari bundling produk utama dengan item pelengkap, atau promo jam sepi. Sebelum jalan, hitung dulu HPP paketnya supaya diskonnya tidak menghabiskan margin."
        )

    if any(keyword in text for keyword in ("stok", "restock", "habis", "persediaan")):
        return (
            f"Untuk urusan stok di {subject}, pakai aturan sederhana dulu, Kak: pisahkan produk cepat laku, sedang, dan lambat."
            f"{product_hint}\n\n"
            "Restock lebih agresif hanya untuk produk cepat laku. Untuk produk lambat, tahan dulu atau buat paket bundling supaya kas tidak terlalu banyak nyangkut di stok."
        )

    if any(keyword in text for keyword in ("supplier", "bahan baku", "vendor")):
        return (
            f"Kalau mau cek supplier untuk {subject}, jangan cuma bandingkan harga satuan, Kak. Bandingkan juga stabilitas stok, ongkir, minimum order, dan konsistensi kualitas.\n\n"
            "Langkah praktis: minta harga dari 2-3 supplier, lalu hitung dampaknya ke HPP produk utama. Kalau selisih HPP lumayan, baru pertimbangkan pindah atau bagi order ke dua supplier."
        )

    return (
        f"Siap, Kak. Untuk {subject}, saya sarankan mulai dari keputusan yang paling dekat dengan uang masuk: harga jual, margin, produk paling laku, dan repeat order."
        f"{product_hint}\n\n"
        "Kalau Kakak mau, kirim satu pertanyaan yang lebih spesifik, misalnya mau cek harga jual, promo, stok, supplier, atau cara naikin penjualan minggu ini."
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

    if payload.intent in {"general_business_advice", "promotion_advice", "restock_advice", "supplier_search"}:
        return _fallback_general_business_answer(payload)

    return (
        "Siap, Kak. Saya bantu dari sisi keputusan bisnisnya ya. Coba ceritakan konteksnya sedikit: produk apa, kondisi sekarang seperti apa, dan target Kakak ingin menaikkan penjualan, menjaga margin, atau mengatur stok?"
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
