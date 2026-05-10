from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Customer, WhatsAppMessage
from app.schemas.enums import CustomerStatus
from app.schemas.telegram import TelegramInboundRequest
from app.services.customer_service import get_customer_by_phone


def _display_name(payload: TelegramInboundRequest) -> str | None:
    parts = [payload.first_name, payload.last_name]
    name = " ".join(part for part in parts if part)
    return name or payload.username


def _telegram_customer_key(chat_id: str) -> str:
    return f"telegram:{chat_id}"


def handle_inbound_message(db: Session, payload: TelegramInboundRequest) -> tuple[str, str]:
    customer_key = _telegram_customer_key(payload.chat_id)
    customer = get_customer_by_phone(db, customer_key)

    if customer is None:
        customer = Customer(
            name=_display_name(payload),
            phone_number=customer_key,
            status=CustomerStatus.PROFILING.value,
            last_active_at=datetime.now(UTC),
        )
        db.add(customer)
        db.flush()
    else:
        if not customer.name:
            customer.name = _display_name(payload)
        customer.last_active_at = datetime.now(UTC)
        if customer.status in {CustomerStatus.REGISTERED.value, CustomerStatus.INVITED.value}:
            customer.status = CustomerStatus.PROFILING.value

    db.add(
        WhatsAppMessage(
            customer_id=customer.id,
            direction="inbound",
            message_text=payload.message_text,
            message_type="telegram_text",
            wa_message_id=f"telegram:{payload.chat_id}:{payload.telegram_message_id}",
            raw_payload=payload.raw_payload,
        )
    )
    db.add(customer)
    db.commit()

    return "Mantap Kak. Nama bisnisnya apa ya?", customer.status
