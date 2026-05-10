from decimal import Decimal

from app.ai.database_mapper import extract_database_mapping


def test_extract_database_mapping_from_business_message():
    mapping = extract_database_mapping(
        "Saya jual ayam geprek di Bandung, harga jualnya 18 ribu, HPP sekitar 11.500."
    )

    assert mapping.business["business_category"] == "kuliner"
    assert mapping.business["location"] == "Bandung"
    assert mapping.products[0].name == "ayam geprek"
    assert mapping.products[0].selling_price == Decimal("18000")
    assert mapping.products[0].hpp == Decimal("11500")
    assert mapping.products[0].margin_percent == Decimal("36.11")
    assert mapping.memories[0].key == "main_product"
    assert mapping.memories[0].value == "ayam geprek"


def test_extract_database_mapping_ignores_prices_without_product():
    mapping = extract_database_mapping("harga jual 18000 hpp 11500")

    assert mapping.business == {}
    assert mapping.products == []
    assert mapping.memories == []
    assert mapping.ignored == ["product_price_without_product_name"]
