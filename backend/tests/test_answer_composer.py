from decimal import Decimal

from app.ai.answer_composer import AnswerComposerInput, compose_fallback_answer


def test_fallback_margin_answer_uses_business_context():
    answer = compose_fallback_answer(
        AnswerComposerInput(
            user_message="HPP ayam geprek saya 11.500, jual 18.000 masih aman nggak?",
            intent="margin_calculation",
            customer={"name": "Budi"},
            business={
                "business_name": "Ayam Geprek Mas Budi",
                "business_category": "kuliner",
                "known_products": ["ayam geprek"],
            },
            conversation_state="ACTIVE",
            tool_results={
                "margin_calculation": {
                    "selling_price": Decimal("18000"),
                    "hpp": Decimal("11500"),
                    "margin_amount": Decimal("6500"),
                    "margin_percent": Decimal("36.11"),
                    "status": "healthy",
                    "recommendation": "Margin masih aman jika target 30%.",
                }
            },
        )
    )

    assert "Ayam Geprek Mas Budi" in answer
    assert "Rp11.500" in answer
    assert "Rp18.000" in answer
    assert "36,11%" in answer
    assert "kemasan" in answer


def test_fallback_recommend_price_answer_is_natural():
    answer = compose_fallback_answer(
        AnswerComposerInput(
            user_message="hpp 11500 target margin 30 harga jual berapa?",
            intent="pricing_advice",
            customer={},
            business={"business_name": "Ayam Geprek Mas Budi"},
            conversation_state="ACTIVE",
            tool_results={
                "recommend_price": {
                    "hpp": Decimal("11500"),
                    "target_margin_percent": Decimal("30"),
                    "minimum_price": Decimal("16429"),
                    "recommended_price_range": [Decimal("17000"), Decimal("19000")],
                }
            },
        )
    )

    assert "Ayam Geprek Mas Budi" in answer
    assert "Rp11.500" in answer
    assert "Rp16.429" in answer
    assert "Rp17.000-Rp19.000" in answer


def test_fallback_general_business_answer_acts_like_mentor():
    answer = compose_fallback_answer(
        AnswerComposerInput(
            user_message="jualan saya lagi sepi, harus gimana?",
            intent="general_business_advice",
            customer={"name": "Budi"},
            business={
                "business_name": "Ayam Geprek Mas Budi",
                "business_category": "kuliner",
                "known_products": ["ayam geprek", "es teh"],
            },
            conversation_state="ACTIVE",
        )
    )

    assert "Ayam Geprek Mas Budi" in answer
    assert "ayam geprek" in answer
    assert "jangan langsung banting harga" in answer
    assert "7 hari terakhir" in answer


def test_fallback_promotion_answer_mentions_margin():
    answer = compose_fallback_answer(
        AnswerComposerInput(
            user_message="mau bikin promo bundling",
            intent="promotion_advice",
            customer={},
            business={"business_name": "Kopi Budi", "business_category": "coffee_shop"},
            conversation_state="ACTIVE",
        )
    )

    assert "Kopi Budi" in answer
    assert "bundling" in answer
    assert "margin" in answer
