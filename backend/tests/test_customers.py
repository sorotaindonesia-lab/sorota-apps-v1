def test_create_list_get_and_update_customer(client):
    create_response = client.post(
        "/api/customers",
        json={
            "name": "Budi",
            "phone_number": "+628123456789",
            "business_name": "Ayam Geprek Mas Budi",
            "business_category": "kuliner",
            "location": "Bandung",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "registered"

    list_response = client.get("/api/customers", params={"business_category": "kuliner"})
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["phone_number"] == "+628123456789"

    detail_response = client.get(f"/api/customers/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["business"]["business_name"] == "Ayam Geprek Mas Budi"

    update_response = client.patch(
        f"/api/customers/{created['id']}",
        json={"status": "active", "location": "Jakarta"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "active"
    assert update_response.json()["business"]["location"] == "Jakarta"


def test_duplicate_customer_phone_returns_conflict(client):
    payload = {"phone_number": "+628111111111"}

    assert client.post("/api/customers", json=payload).status_code == 201
    assert client.post("/api/customers", json=payload).status_code == 409
