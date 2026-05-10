from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import EarlyWarningEvent
from app.schemas.early_warning import EarlyWarningEventRead, EarlyWarningListResponse
from app.services.early_warning_service import (
    approve_early_warning_event,
    get_early_warning_event,
    list_early_warning_events,
    mark_early_warning_event_sent,
)

router = APIRouter(prefix="/api/early-warnings", tags=["early-warnings"])


def _to_read(event: EarlyWarningEvent) -> EarlyWarningEventRead:
    return EarlyWarningEventRead(
        id=event.id,
        customer_id=event.customer_id,
        business_id=event.business_id,
        rule_id=event.rule_id,
        severity=event.severity,
        title=event.title,
        message=event.message,
        evidence=event.evidence,
        status=event.status,
        scheduled_send_at=event.scheduled_send_at,
        sent_at=event.sent_at,
        created_at=event.created_at,
    )


@router.get("", response_model=EarlyWarningListResponse)
def list_early_warnings_endpoint(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> EarlyWarningListResponse:
    events = list_early_warning_events(db, status=status_filter, limit=limit, offset=offset)
    return EarlyWarningListResponse(items=[_to_read(event) for event in events])


@router.post("/{event_id}/approve", response_model=EarlyWarningEventRead)
def approve_early_warning_endpoint(event_id: UUID, db: Session = Depends(get_db)) -> EarlyWarningEventRead:
    event = get_early_warning_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="early warning event not found")
    return _to_read(approve_early_warning_event(db, event))


@router.post("/{event_id}/send", response_model=EarlyWarningEventRead)
def send_early_warning_endpoint(event_id: UUID, db: Session = Depends(get_db)) -> EarlyWarningEventRead:
    event = get_early_warning_event(db, event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="early warning event not found")
    return _to_read(mark_early_warning_event_sent(db, event))
