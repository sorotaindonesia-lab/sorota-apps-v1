from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Customer, WhatsAppMessage
from app.schemas.enums import ConversationState, CustomerStatus
from app.schemas.whatsapp import WhatsAppInboundRequest
from app.services.business_assistant_service import answer_active_message
from app.services.customer_service import get_customer_by_phone
from app.services.profiling_service import advance_profiling


def _log_outbound_message(db: Session, customer: Customer, reply_text: str) -> None:
    db.add(
        WhatsAppMessage(
            customer_id=customer.id,
            direction="outbound",
            message_text=reply_text,
            message_type="text",
            raw_payload={"channel": "whatsapp"},
        )
    )


def handle_inbound_message(db: Session, payload: WhatsAppInboundRequest) -> tuple[str, str]:
    customer = get_customer_by_phone(db, payload.phone_number)
    if customer is None:
        customer = Customer(
            phone_number=payload.phone_number,
            status=CustomerStatus.PROFILING.value,
            conversation_state=ConversationState.NEW.value,
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
    if customer.conversation_state == ConversationState.ACTIVE.value:
        assistant_reply = answer_active_message(payload.message_text)
        reply_text = assistant_reply.reply_text
        customer.status = CustomerStatus.ACTIVE.value
    else:
        result = advance_profiling(db, customer, payload.message_text)
        reply_text = result.reply_text

    _log_outbound_message(db, customer, reply_text)
    db.commit()

    return reply_text, customer.status
