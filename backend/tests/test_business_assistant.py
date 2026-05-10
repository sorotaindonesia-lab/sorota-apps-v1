from decimal import Decimal

from app.services.business_assistant_service import (
    answer_active_message,
    parse_margin_request,
    parse_recommend_price_request,
)


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


def test_parse_recommend_price_request_with_target_margin():
    request = parse_recommend_price_request("hpp 11500 target margin 30 harga jual berapa?")

    assert request is not None
    assert request.hpp == Decimal("11500")
    assert request.target_margin_percent == Decimal("30")


def test_parse_recommend_price_request_with_rupiah_and_percent():
    request = parse_recommend_price_request("Modal Rp11.500, target margin 30% saran harga jual berapa?")

    assert request is not None
    assert request.hpp == Decimal("11500")
    assert request.target_margin_percent == Decimal("30")


def test_answer_active_message_returns_recommend_price_reply():
    reply = answer_active_message("hpp 11500 target margin 30 harga jual berapa?")

    assert reply.handled is True
    assert "Rp11.500" in reply.reply_text
    assert "30,00%" in reply.reply_text
    assert "Rp16.429" in reply.reply_text
    assert "Rp17.000-Rp19.000" in reply.reply_text
