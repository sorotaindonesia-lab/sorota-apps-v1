def test_inbound_whatsapp_creates_or_updates_customer(client):
    response = client.post(
        "/internal/whatsapp/inbound",
        json={
            "phone_number": "+628999999999",
            "message_text": "Saya jual ayam geprek di Bandung",
            "wa_message_id": "wamid.test",
            "raw_payload": {"source": "test"},
        },
    )

    assert response.status_code == 200
    assert response.json()["should_send"] is True
    assert response.json()["customer_status"] == "profiling"

    customers = client.get("/api/customers").json()["items"]
    assert customers[0]["phone_number"] == "+628999999999"
