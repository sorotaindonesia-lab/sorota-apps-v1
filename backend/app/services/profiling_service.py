from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models import Business, Customer, Product
from app.schemas.enums import ConversationState, CustomerStatus


CATEGORY_MENU = """Bisnis Kakak masuk kategori apa?

1. Kuliner
2. Retail
3. Fashion
4. Laundry
5. Warung
6. Toko kelontong
7. Coffee shop
8. Reseller
9. Jasa
10. Lainnya"""


@dataclass(frozen=True)
class ProfilingResult:
    reply_text: str
    customer_status: str
    conversation_state: str


def _clean_text(value: str | None) -> str:
    return (value or "").strip()


def _get_or_create_business(db: Session, customer: Customer) -> Business:
    if customer.businesses:
        return customer.businesses[0]

    business = Business(customer_id=customer.id)
    db.add(business)
    db.flush()
    customer.businesses.append(business)
    return business


def _parse_category(value: str) -> str | None:
    normalized = value.strip().lower().replace(".", "").replace("-", " ").replace("_", " ")
    by_number = {
        "1": "kuliner",
        "2": "retail",
        "3": "fashion",
        "4": "laundry",
        "5": "warung",
        "6": "toko_kelontong",
        "7": "coffee_shop",
        "8": "reseller",
        "9": "jasa",
        "10": "lainnya",
    }
    if normalized in by_number:
        return by_number[normalized]

    aliases = {
        "kuliner": "kuliner",
        "makanan": "kuliner",
        "minuman": "kuliner",
        "retail": "retail",
        "fashion": "fashion",
        "laundry": "laundry",
        "warung": "warung",
        "toko kelontong": "toko_kelontong",
        "kelontong": "toko_kelontong",
        "coffee shop": "coffee_shop",
        "coffeeshop": "coffee_shop",
        "kopi": "coffee_shop",
        "reseller": "reseller",
        "jasa": "jasa",
        "lainnya": "lainnya",
        "lain": "lainnya",
    }
    if normalized in aliases:
        return aliases[normalized]

    for alias, category in aliases.items():
        if alias in normalized:
            return category

    return None


def _split_products(value: str) -> list[str]:
    separators = [",", "\n", ";"]
    items = [value]
    for separator in separators:
        next_items: list[str] = []
        for item in items:
            next_items.extend(item.split(separator))
        items = next_items

    return [item.strip() for item in items if item.strip()]


def _save_products(db: Session, business: Business, value: str) -> None:
    products = _split_products(value)
    if not products:
        return

    existing_names = {product.name.lower() for product in business.products}
    for product_name in products:
        if product_name.lower() in existing_names:
            continue
        db.add(Product(business_id=business.id, name=product_name))
        existing_names.add(product_name.lower())


def _ask_business_name(customer: Customer) -> ProfilingResult:
    customer.status = CustomerStatus.PROFILING.value
    customer.conversation_state = ConversationState.ASK_BUSINESS_NAME.value
    return ProfilingResult(
        reply_text="Halo Kak, saya Sorota. Biar saya bisa bantu lebih tepat, boleh tahu nama bisnis Kakak?",
        customer_status=customer.status,
        conversation_state=customer.conversation_state,
    )


def advance_profiling(db: Session, customer: Customer, message_text: str | None) -> ProfilingResult:
    text = _clean_text(message_text)
    state = customer.conversation_state or ConversationState.NEW.value

    if state == ConversationState.NEW.value:
        return _ask_business_name(customer)

    if state == ConversationState.ASK_BUSINESS_NAME.value:
        if not text:
            return ProfilingResult(
                reply_text="Boleh tahu nama bisnis Kakak?",
                customer_status=customer.status,
                conversation_state=customer.conversation_state,
            )

        business = _get_or_create_business(db, customer)
        business.business_name = text
        customer.status = CustomerStatus.PROFILING.value
        customer.conversation_state = ConversationState.ASK_BUSINESS_CATEGORY.value
        return ProfilingResult(
            reply_text=CATEGORY_MENU,
            customer_status=customer.status,
            conversation_state=customer.conversation_state,
        )

    if state == ConversationState.ASK_BUSINESS_CATEGORY.value:
        category = _parse_category(text)
        if category is None:
            return ProfilingResult(
                reply_text=f"Saya belum bisa mengenali kategori itu. Pilih angka atau tulis salah satu kategori ya.\n\n{CATEGORY_MENU}",
                customer_status=customer.status,
                conversation_state=customer.conversation_state,
            )

        business = _get_or_create_business(db, customer)
        business.business_category = category
        customer.status = CustomerStatus.PROFILING.value
        customer.conversation_state = ConversationState.ASK_LOCATION.value
        return ProfilingResult(
            reply_text="Lokasi bisnis Kakak di kota atau area mana?",
            customer_status=customer.status,
            conversation_state=customer.conversation_state,
        )

    if state == ConversationState.ASK_LOCATION.value:
        if not text:
            return ProfilingResult(
                reply_text="Lokasi bisnis Kakak di kota atau area mana?",
                customer_status=customer.status,
                conversation_state=customer.conversation_state,
            )

        business = _get_or_create_business(db, customer)
        business.location = text
        customer.status = CustomerStatus.PROFILING.value
        customer.conversation_state = ConversationState.ASK_MAIN_PRODUCTS.value
        return ProfilingResult(
            reply_text="Produk utama yang paling sering Kakak jual apa? Boleh sebut satu atau beberapa, pisahkan dengan koma.",
            customer_status=customer.status,
            conversation_state=customer.conversation_state,
        )

    if state == ConversationState.ASK_MAIN_PRODUCTS.value:
        if not text:
            return ProfilingResult(
                reply_text="Produk utama yang paling sering Kakak jual apa?",
                customer_status=customer.status,
                conversation_state=customer.conversation_state,
            )

        business = _get_or_create_business(db, customer)
        _save_products(db, business, text)
        customer.status = CustomerStatus.ACTIVE.value
        customer.conversation_state = ConversationState.ACTIVE.value
        return ProfilingResult(
            reply_text=(
                "Siap Kak. Data bisnis awal sudah saya simpan.\n\n"
                "Mulai sekarang Kakak bisa tanya soal harga jual, margin, HPP, supplier, atau strategi bisnis harian."
            ),
            customer_status=customer.status,
            conversation_state=customer.conversation_state,
        )

    customer.status = CustomerStatus.ACTIVE.value
    customer.conversation_state = ConversationState.ACTIVE.value
    return ProfilingResult(
        reply_text="Siap Kak. Untuk tahap ini, saya sudah aktif dan siap bantu pertanyaan bisnis harian Kakak.",
        customer_status=customer.status,
        conversation_state=customer.conversation_state,
    )
