from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.whatsapp import WhatsAppInboundRequest, WhatsAppInboundResponse
from app.services.whatsapp_service import handle_inbound_message

router = APIRouter(prefix="/internal/whatsapp", tags=["internal-whatsapp"])


@router.post("/inbound", response_model=WhatsAppInboundResponse)
def inbound_message(
    payload: WhatsAppInboundRequest,
    db: Session = Depends(get_db),
) -> WhatsAppInboundResponse:
    reply_text, customer_status = handle_inbound_message(db, payload)
    return WhatsAppInboundResponse(
        reply_text=reply_text,
        should_send=True,
        customer_status=customer_status,
    )
