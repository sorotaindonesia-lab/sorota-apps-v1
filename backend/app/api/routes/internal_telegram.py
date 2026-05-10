from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.telegram import TelegramInboundRequest, TelegramInboundResponse
from app.services.telegram_service import handle_inbound_message

router = APIRouter(prefix="/internal/telegram", tags=["internal-telegram"])


@router.post("/inbound", response_model=TelegramInboundResponse)
def inbound_message(
    payload: TelegramInboundRequest,
    db: Session = Depends(get_db),
) -> TelegramInboundResponse:
    reply_text, customer_status = handle_inbound_message(db, payload)
    return TelegramInboundResponse(
        reply_text=reply_text,
        should_send=True,
        customer_status=customer_status,
    )
