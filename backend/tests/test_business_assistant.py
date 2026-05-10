from decimal import Decimal

from app.services.business_assistant_service import answer_active_message, parse_margin_request


def test_parse_margin_request_with_labels():
    request = parse_margin_request("harga jual 18000 hpp 11500 margin berapa?")

    assert request is not None
    assert request.selling_price == Decimal("18000")
    assert request.hpp == Decimal("11500")


def test_parse_margin_request_with_rupiah_format():
    request = parse_margin_request("Harga jual Rp18.000, HPP Rp11.500")

    assert request is not None
    assert request.selling_price == Decimal("18000")
    assert request.hpp == Decimal("11500")


def test_answer_active_message_returns_margin_reply():
    reply = answer_active_message("harga jual 18000 hpp 11500 margin berapa?")

    assert reply.handled is True
    assert "Rp18.000" in reply.reply_text
    assert "Rp11.500" in reply.reply_text
    assert "Rp6.500" in reply.reply_text
    assert "36,11%" in reply.reply_text
