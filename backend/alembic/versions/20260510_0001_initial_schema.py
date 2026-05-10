"""initial schema

Revision ID: 20260510_0001
Revises:
Create Date: 2026-05-10 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260510_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "admins",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("role", sa.String(), nullable=False, server_default="admin"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.Column("status", sa.String(), server_default="registered", nullable=False),
        sa.Column("created_by_admin_id", sa.Uuid(), nullable=True),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["admins.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number"),
    )

    op.create_table(
        "businesses",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("business_name", sa.String(), nullable=True),
        sa.Column("business_category", sa.String(), nullable=True),
        sa.Column("business_subcategory", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("business_stage", sa.String(), nullable=True),
        sa.Column("target_margin_percent", sa.Numeric(6, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("selling_price", sa.Numeric(14, 2), nullable=True),
        sa.Column("hpp", sa.Numeric(14, 2), nullable=True),
        sa.Column("margin_percent", sa.Numeric(6, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "whatsapp_messages",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=True),
        sa.Column("direction", sa.String(), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=True),
        sa.Column("message_type", sa.String(), server_default="text", nullable=False),
        sa.Column("wa_message_id", sa.String(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(), server_default="active", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "user_memories",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("memory_key", sa.String(), nullable=False),
        sa.Column("memory_value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True, server_default="0.8"),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id", "memory_key", name="uq_user_memories_customer_memory_key"),
    )

    op.create_table(
        "recommendations",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("business_id", sa.Uuid(), nullable=True),
        sa.Column("recommendation_type", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("action_items", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ai_usage_logs",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=True),
        sa.Column("task_type", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=True),
        sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=True),
        sa.Column("cached_tokens", sa.Integer(), server_default="0", nullable=True),
        sa.Column("cost_estimate_usd", sa.Numeric(12, 6), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("prompt_version", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "knowledge_documents",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("business_category", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("source_type", sa.String(), nullable=True),
        sa.Column("source_url", sa.String(), nullable=True),
        sa.Column("confidence_score", sa.Numeric(4, 3), nullable=True, server_default="0.8"),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_admin_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["admins.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "training_examples",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("ideal_answer", sa.Text(), nullable=False),
        sa.Column("business_category", sa.String(), nullable=True),
        sa.Column("intent", sa.String(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "bot_rules",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("rule_name", sa.String(), nullable=False),
        sa.Column("rule_content", sa.Text(), nullable=False),
        sa.Column("scope", sa.String(), server_default="global", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "bot_skills",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("skill_name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_name"),
    )

    op.create_table(
        "response_feedback",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("message_id", sa.Uuid(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("feedback_type", sa.String(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_admin_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["admins.id"]),
        sa.ForeignKeyConstraint(["message_id"], ["whatsapp_messages.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "early_warning_rules",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("business_category", sa.String(), nullable=True),
        sa.Column("rule_type", sa.String(), nullable=False),
        sa.Column("threshold_config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "early_warning_events",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=True),
        sa.Column("business_id", sa.Uuid(), nullable=True),
        sa.Column("rule_id", sa.Uuid(), nullable=True),
        sa.Column("severity", sa.String(), server_default="info", nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(), server_default="draft", nullable=False),
        sa.Column("scheduled_send_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_id"], ["early_warning_rules.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_customers_status", "customers", ["status"])
    op.create_index("idx_customers_phone_number", "customers", ["phone_number"])
    op.create_index("idx_businesses_customer_id", "businesses", ["customer_id"])
    op.create_index("idx_businesses_category", "businesses", ["business_category"])
    op.create_index("idx_products_business_id", "products", ["business_id"])
    op.create_index("idx_whatsapp_messages_customer_created", "whatsapp_messages", ["customer_id", sa.text("created_at DESC")])
    op.create_index("idx_ai_usage_created", "ai_usage_logs", [sa.text("created_at DESC")])
    op.create_index("idx_knowledge_category", "knowledge_documents", ["category", "business_category"])
    op.create_index("idx_early_warning_events_customer", "early_warning_events", ["customer_id", sa.text("created_at DESC")])
    op.create_index("idx_early_warning_events_status", "early_warning_events", ["status"])

    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = now();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    for table_name in (
        "admins",
        "customers",
        "businesses",
        "products",
        "user_memories",
        "knowledge_documents",
        "bot_rules",
        "early_warning_rules",
    ):
        op.execute(
            f"""
            DROP TRIGGER IF EXISTS trg_{table_name}_updated_at ON {table_name};
            CREATE TRIGGER trg_{table_name}_updated_at
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table_name in (
        "early_warning_rules",
        "bot_rules",
        "knowledge_documents",
        "user_memories",
        "products",
        "businesses",
        "customers",
        "admins",
    ):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table_name}_updated_at ON {table_name}")

    op.drop_index("idx_early_warning_events_status", table_name="early_warning_events")
    op.drop_index("idx_early_warning_events_customer", table_name="early_warning_events")
    op.drop_index("idx_knowledge_category", table_name="knowledge_documents")
    op.drop_index("idx_ai_usage_created", table_name="ai_usage_logs")
    op.drop_index("idx_whatsapp_messages_customer_created", table_name="whatsapp_messages")
    op.drop_index("idx_products_business_id", table_name="products")
    op.drop_index("idx_businesses_category", table_name="businesses")
    op.drop_index("idx_businesses_customer_id", table_name="businesses")
    op.drop_index("idx_customers_phone_number", table_name="customers")
    op.drop_index("idx_customers_status", table_name="customers")

    op.drop_table("early_warning_events")
    op.drop_table("early_warning_rules")
    op.drop_table("response_feedback")
    op.drop_table("bot_skills")
    op.drop_table("bot_rules")
    op.drop_table("training_examples")
    op.drop_table("knowledge_documents")
    op.drop_table("ai_usage_logs")
    op.drop_table("recommendations")
    op.drop_table("user_memories")
    op.drop_table("chat_sessions")
    op.drop_table("whatsapp_messages")
    op.drop_table("products")
    op.drop_table("businesses")
    op.drop_table("customers")
    op.drop_table("admins")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")
