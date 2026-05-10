from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Customer, WhatsAppMessage
from app.schemas.enums import CustomerStatus
from app.schemas.whatsapp import WhatsAppInboundRequest
from app.services.customer_service import get_customer_by_phone


def handle_inbound_message(db: Session, payload: WhatsAppInboundRequest) -> tuple[str, str]:
    customer = get_customer_by_phone(db, payload.phone_number)
    if customer is None:
        customer = Customer(
            phone_number=payload.phone_number,
            status=CustomerStatus.PROFILING.value,
            last_active_at=datetime.now(UTC),
        )
        db.add(customer)
        db.flush()
    else:
        customer.last_active_at = datetime.now(UTC)
        if customer.status in {CustomerStatus.REGISTERED.value, CustomerStatus.INVITED.value}:
            customer.status = CustomerStatus.PROFILING.value

    db.add(
        WhatsAppMessage(
            customer_id=customer.id,
            direction="inbound",
            message_text=payload.message_text,
            message_type="text",
            wa_message_id=payload.wa_message_id,
            raw_payload=payload.raw_payload,
        )
    )
    db.add(customer)
    db.commit()

    return "Mantap Kak. Nama bisnisnya apa ya?", customer.status
