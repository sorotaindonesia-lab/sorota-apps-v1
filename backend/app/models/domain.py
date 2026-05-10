import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def json_type():
    return JSON().with_variant(postgresql.JSONB, "postgresql")


def tags_type():
    return JSON().with_variant(postgresql.ARRAY(String), "postgresql")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Admin(Base, TimestampMixin):
    __tablename__ = "admins"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, nullable=False, default="admin")


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"
    __table_args__ = (
        Index("idx_customers_status", "status"),
        Index("idx_customers_phone_number", "phone_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="registered")
    created_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("admins.id"),
    )
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    businesses: Mapped[list["Business"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["WhatsAppMessage"]] = relationship(back_populates="customer")


class Business(Base, TimestampMixin):
    __tablename__ = "businesses"
    __table_args__ = (
        Index("idx_businesses_customer_id", "customer_id"),
        Index("idx_businesses_category", "business_category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    business_name: Mapped[str | None] = mapped_column(String)
    business_category: Mapped[str | None] = mapped_column(String)
    business_subcategory: Mapped[str | None] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String)
    business_stage: Mapped[str | None] = mapped_column(String)
    target_margin_percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    customer: Mapped[Customer] = relationship(back_populates="businesses")
    products: Mapped[list["Product"]] = relationship(back_populates="business", cascade="all, delete-orphan")


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (Index("idx_products_business_id", "business_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str | None] = mapped_column(String)
    selling_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    hpp: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    margin_percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    business: Mapped[Business] = relationship(back_populates="products")


class WhatsAppMessage(Base):
    __tablename__ = "whatsapp_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
    )
    direction: Mapped[str] = mapped_column(String, nullable=False)
    message_text: Mapped[str | None] = mapped_column(Text)
    message_type: Mapped[str] = mapped_column(String, nullable=False, default="text")
    wa_message_id: Mapped[str | None] = mapped_column(String)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    customer: Mapped[Customer | None] = relationship(back_populates="messages")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class UserMemory(Base, TimestampMixin):
    __tablename__ = "user_memories"
    __table_args__ = (
        UniqueConstraint("customer_id", "memory_key", name="uq_user_memories_customer_memory_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    memory_key: Mapped[str] = mapped_column(String, nullable=False)
    memory_value: Mapped[dict[str, Any]] = mapped_column(json_type(), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), default=Decimal("0.8"))
    source: Mapped[str | None] = mapped_column(String)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    business_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="SET NULL"),
    )
    recommendation_type: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    action_items: Mapped[list[dict[str, Any]] | None] = mapped_column(json_type())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AiUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
    )
    task_type: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cached_tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost_estimate_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    prompt_version: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class KnowledgeDocument(Base, TimestampMixin):
    __tablename__ = "knowledge_documents"
    __table_args__ = (Index("idx_knowledge_category", "category", "business_category"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String)
    business_category: Mapped[str | None] = mapped_column(String)
    location: Mapped[str | None] = mapped_column(String)
    source_type: Mapped[str | None] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(String)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 3), default=Decimal("0.8"))
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("admins.id"),
    )


class TrainingExample(Base):
    __tablename__ = "training_examples"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    ideal_answer: Mapped[str] = mapped_column(Text, nullable=False)
    business_category: Mapped[str | None] = mapped_column(String)
    intent: Mapped[str | None] = mapped_column(String)
    tags: Mapped[list[str] | None] = mapped_column(tags_type())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class BotRule(Base, TimestampMixin):
    __tablename__ = "bot_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_name: Mapped[str] = mapped_column(String, nullable=False)
    rule_content: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False, default="global")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class BotSkill(Base):
    __tablename__ = "bot_skills"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    skill_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ResponseFeedback(Base):
    __tablename__ = "response_feedback"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("whatsapp_messages.id", ondelete="SET NULL"),
    )
    rating: Mapped[int | None] = mapped_column(Integer)
    feedback_type: Mapped[str | None] = mapped_column(String)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("admins.id"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class EarlyWarningRule(Base, TimestampMixin):
    __tablename__ = "early_warning_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    business_category: Mapped[str | None] = mapped_column(String)
    rule_type: Mapped[str] = mapped_column(String, nullable=False)
    threshold_config: Mapped[dict[str, Any]] = mapped_column(json_type(), nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class EarlyWarningEvent(Base):
    __tablename__ = "early_warning_events"
    __table_args__ = (Index("idx_early_warning_events_status", "status"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
    )
    business_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="SET NULL"),
    )
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("early_warning_rules.id", ondelete="SET NULL"),
    )
    severity: Mapped[str] = mapped_column(String, nullable=False, default="info")
    title: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict[str, Any] | None] = mapped_column(json_type())
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    scheduled_send_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


Index("idx_whatsapp_messages_customer_created", WhatsAppMessage.customer_id, WhatsAppMessage.created_at.desc())
Index("idx_ai_usage_created", AiUsageLog.created_at.desc())
Index("idx_early_warning_events_customer", EarlyWarningEvent.customer_id, EarlyWarningEvent.created_at.desc())
