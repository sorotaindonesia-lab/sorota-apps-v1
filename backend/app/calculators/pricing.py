from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def calculate_margin(selling_price: Decimal, hpp: Decimal) -> dict[str, object]:
    if selling_price <= 0:
        raise ValueError("selling_price must be greater than zero")
    if hpp < 0:
        raise ValueError("hpp must be zero or greater")

    margin_amount = selling_price - hpp
    margin_percent = (margin_amount / selling_price * Decimal("100")).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    status = "healthy" if margin_percent >= Decimal("30") else "thin"

    return {
        "margin_amount": _money(margin_amount),
        "margin_percent": margin_percent,
        "status": status,
        "recommendation": "Margin masih aman jika target 30%."
        if status == "healthy"
        else "Margin tipis jika target 30%. Cek HPP atau pertimbangkan harga jual baru.",
    }


def recommend_price(hpp: Decimal, target_margin_percent: Decimal) -> dict[str, object]:
    if hpp < 0:
        raise ValueError("hpp must be zero or greater")
    if target_margin_percent <= 0 or target_margin_percent >= 100:
        raise ValueError("target_margin_percent must be between 0 and 100")

    minimum_price = hpp / (Decimal("1") - (target_margin_percent / Decimal("100")))
    minimum_price = _money(minimum_price)
    lower_bound = _money((minimum_price / Decimal("1000")).to_integral_value(rounding=ROUND_CEILING) * Decimal("1000"))
    upper_bound = _money(lower_bound + Decimal("2000"))

    return {
        "minimum_price": minimum_price,
        "recommended_price_range": [lower_bound, upper_bound],
        "explanation": f"Harga minimal untuk margin {target_margin_percent}% sekitar Rp{minimum_price}.",
    }
