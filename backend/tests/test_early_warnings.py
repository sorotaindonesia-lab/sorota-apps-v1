from app.db.session import get_db
from app.models import EarlyWarningEvent


def test_early_warning_list_approve_and_send(client):
    override = client.app.dependency_overrides[get_db]
    db = next(override())
    try:
        event = EarlyWarningEvent(
            severity="warning",
            title="Harga bahan naik",
            message="Cek ulang HPP hari ini.",
            status="draft",
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        event_id = str(event.id)
    finally:
        db.close()

    list_response = client.get("/api/early-warnings", params={"status": "draft"})
    assert list_response.status_code == 200
    assert list_response.json()["items"][0]["id"] == event_id

    approve_response = client.post(f"/api/early-warnings/{event_id}/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    send_response = client.post(f"/api/early-warnings/{event_id}/send")
    assert send_response.status_code == 200
    assert send_response.json()["status"] == "sent"
    assert send_response.json()["sent_at"] is not None
