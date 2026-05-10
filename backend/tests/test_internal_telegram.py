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
