from decimal import Decimal

from app.calculators import calculate_margin, recommend_price


def test_calculate_margin():
    result = calculate_margin(Decimal("18000"), Decimal("11500"))

    assert result["margin_amount"] == Decimal("6500")
    assert result["margin_percent"] == Decimal("36.11")
    assert result["status"] == "healthy"


def test_recommend_price():
    result = recommend_price(Decimal("11500"), Decimal("30"))

    assert result["minimum_price"] == Decimal("16429")
    assert result["recommended_price_range"] == [Decimal("17000"), Decimal("19000")]
