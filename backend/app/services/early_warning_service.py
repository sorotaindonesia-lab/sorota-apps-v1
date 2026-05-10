from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EarlyWarningEvent


def list_early_warning_events(
    db: Session,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[EarlyWarningEvent]:
    stmt = select(EarlyWarningEvent)
    if status:
        stmt = stmt.where(EarlyWarningEvent.status == status)
    stmt = stmt.order_by(EarlyWarningEvent.created_at.desc()).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def get_early_warning_event(db: Session, event_id: UUID) -> EarlyWarningEvent | None:
    return db.get(EarlyWarningEvent, event_id)


def approve_early_warning_event(db: Session, event: EarlyWarningEvent) -> EarlyWarningEvent:
    event.status = "approved"
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def mark_early_warning_event_sent(db: Session, event: EarlyWarningEvent) -> EarlyWarningEvent:
    event.status = "sent"
    event.sent_at = datetime.now(UTC)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
