from sqlalchemy import select

from app.db.session import get_db
from app.models import Product, WhatsAppMessage


def test_inbound_telegram_creates_customer_with_channel_key(client):
    response = client.post(
        "/internal/telegram/inbound",
        json={
            "telegram_user_id": "12345",
            "chat_id": "67890",
            "username": "budi_umkm",
            "first_name": "Budi",
            "message_text": "Saya jual ayam geprek di Bandung",
            "telegram_message_id": "11",
            "raw_payload": {"update_id": 1},
        },
    )

    assert response.status_code == 200
    assert response.json()["should_send"] is True
    assert response.json()["customer_status"] == "profiling"

    customers = client.get("/api/customers").json()["items"]
    assert customers[0]["phone_number"] == "telegram:67890"
    assert customers[0]["name"] == "Budi"
    assert customers[0]["conversation_state"] == "ASK_BUSINESS_NAME"


def test_telegram_profiling_state_machine(client):
    def send(text: str, message_id: int):
        return client.post(
            "/internal/telegram/inbound",
            json={
                "telegram_user_id": "12345",
                "chat_id": "11111",
                "first_name": "Budi",
                "message_text": text,
                "telegram_message_id": str(message_id),
                "raw_payload": {"update_id": message_id},
            },
        )

    first = send("Halo", 1)
    assert first.status_code == 200
    assert "nama bisnis" in first.json()["reply_text"].lower()

    customer = client.get("/api/customers").json()["items"][0]
    assert customer["status"] == "profiling"
    assert customer["conversation_state"] == "ASK_BUSINESS_NAME"

    second = send("Ayam Geprek Mas Budi", 2)
    assert second.status_code == 200
    assert "kategori" in second.json()["reply_text"].lower()

    customer_id = client.get("/api/customers").json()["items"][0]["id"]
    detail = client.get(f"/api/customers/{customer_id}").json()
    assert detail["conversation_state"] == "ASK_BUSINESS_CATEGORY"
    assert detail["business"]["business_name"] == "Ayam Geprek Mas Budi"

    third = send("1", 3)
    assert third.status_code == 200
    assert "lokasi" in third.json()["reply_text"].lower()

    detail = client.get(f"/api/customers/{customer_id}").json()
    assert detail["conversation_state"] == "ASK_LOCATION"
    assert detail["business"]["business_category"] == "kuliner"

    fourth = send("Bandung", 4)
    assert fourth.status_code == 200
    assert "produk utama" in fourth.json()["reply_text"].lower()

    detail = client.get(f"/api/customers/{customer_id}").json()
    assert detail["conversation_state"] == "ASK_MAIN_PRODUCTS"
    assert detail["business"]["location"] == "Bandung"

    fifth = send("ayam geprek, es teh", 5)
    assert fifth.status_code == 200
    assert "data bisnis awal" in fifth.json()["reply_text"].lower()

    detail = client.get(f"/api/customers/{customer_id}").json()
    assert detail["status"] == "active"
    assert detail["conversation_state"] == "ACTIVE"

    override = client.app.dependency_overrides[get_db]
    db_generator = override()
    db = next(db_generator)
    try:
        product_names = list(db.scalars(select(Product.name).order_by(Product.name)).all())
    finally:
        db.close()
        db_generator.close()

    assert product_names == ["ayam geprek", "es teh"]


def test_telegram_invalid_category_keeps_state(client):
    client.post(
        "/internal/telegram/inbound",
        json={"chat_id": "22222", "message_text": "Halo", "telegram_message_id": "1"},
    )
    client.post(
        "/internal/telegram/inbound",
        json={"chat_id": "22222", "message_text": "Toko Budi", "telegram_message_id": "2"},
    )
    response = client.post(
        "/internal/telegram/inbound",
        json={"chat_id": "22222", "message_text": "kategori aneh", "telegram_message_id": "3"},
    )

    assert response.status_code == 200
    assert "belum bisa mengenali" in response.json()["reply_text"].lower()

    customer = client.get("/api/customers").json()["items"][0]
    assert customer["conversation_state"] == "ASK_BUSINESS_CATEGORY"


def test_telegram_active_customer_can_calculate_margin(client):
    def send(text: str, message_id: int):
        return client.post(
            "/internal/telegram/inbound",
            json={
                "telegram_user_id": "12345",
                "chat_id": "33333",
                "first_name": "Budi",
                "message_text": text,
                "telegram_message_id": str(message_id),
                "raw_payload": {"update_id": message_id},
            },
        )

    for index, text in enumerate(
        ["Halo", "Ayam Geprek Mas Budi", "kuliner", "Bandung", "ayam geprek"],
        start=1,
    ):
        assert send(text, index).status_code == 200

    response = send("harga jual 18000 hpp 11500 margin berapa?", 6)
    assert response.status_code == 200
    assert response.json()["customer_status"] == "active"
    assert "Rp18.000" in response.json()["reply_text"]
    assert "Rp11.500" in response.json()["reply_text"]
    assert "Rp6.500" in response.json()["reply_text"]
    assert "36,11%" in response.json()["reply_text"]

    customer_id = client.get("/api/customers").json()["items"][0]["id"]
    detail = client.get(f"/api/customers/{customer_id}").json()
    assert detail["conversation_state"] == "ACTIVE"

    override = client.app.dependency_overrides[get_db]
    db_generator = override()
    db = next(db_generator)
    try:
        outbound_messages = list(
            db.scalars(
                select(WhatsAppMessage)
                .where(WhatsAppMessage.direction == "outbound")
                .order_by(WhatsAppMessage.created_at)
            ).all()
        )
    finally:
        db.close()
        db_generator.close()

    assert outbound_messages
    assert "Rp6.500" in outbound_messages[-1].message_text


def test_telegram_active_customer_can_get_recommended_price(client):
    def send(text: str, message_id: int):
        return client.post(
            "/internal/telegram/inbound",
            json={
                "telegram_user_id": "12345",
                "chat_id": "44444",
                "first_name": "Budi",
                "message_text": text,
                "telegram_message_id": str(message_id),
                "raw_payload": {"update_id": message_id},
            },
        )

    for index, text in enumerate(
        ["Halo", "Ayam Geprek Mas Budi", "kuliner", "Bandung", "ayam geprek"],
        start=1,
    ):
        assert send(text, index).status_code == 200

    response = send("hpp 11500 target margin 30 harga jual berapa?", 6)
    assert response.status_code == 200
    assert response.json()["customer_status"] == "active"
    assert "Ayam Geprek Mas Budi" in response.json()["reply_text"]
    assert "Rp11.500" in response.json()["reply_text"]
    assert "30,00%" in response.json()["reply_text"]
    assert "Rp16.429" in response.json()["reply_text"]
    assert "Rp17.000-Rp19.000" in response.json()["reply_text"]
