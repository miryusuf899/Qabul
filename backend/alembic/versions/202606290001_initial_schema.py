"""initial schema

Revision ID: 202606290001
Revises:
Create Date: 2026-06-29
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606290001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


user_role = sa.Enum("platform_admin", "owner", "staff", "client", name="user_role")
booking_status = sa.Enum("pending", "confirmed", "completed", "cancelled", "no_show", name="booking_status")
booking_source = sa.Enum("dashboard", "telegram_ai", "telegram_manual", name="booking_source")
notification_status = sa.Enum("pending", "sent", "failed", name="notification_status")
subscription_plan = sa.Enum("free", "basic", "pro", "business", name="subscription_plan")
subscription_status = sa.Enum("active", "expired", "cancelled", name="subscription_status")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "businesses",
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("business_type", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("logo_url", sa.String(length=1000), nullable=True),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("ai_enabled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], name=op.f("fk_businesses_owner_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_businesses")),
    )
    op.create_index("ix_businesses_is_active", "businesses", ["is_active"], unique=False)
    op.create_index("ix_businesses_owner_id", "businesses", ["owner_id"], unique=False)
    op.create_index(op.f("ix_businesses_id"), "businesses", ["id"], unique=False)

    op.create_table(
        "clients",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("telegram_username", sa.String(length=255), nullable=True),
        sa.Column("total_visits", sa.Integer(), nullable=False),
        sa.Column("last_visit_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_clients_business_id_businesses"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clients")),
        sa.UniqueConstraint("business_id", "telegram_id", name="uq_clients_business_telegram"),
    )
    op.create_index("ix_clients_business_id", "clients", ["business_id"], unique=False)
    op.create_index("ix_clients_telegram_id", "clients", ["telegram_id"], unique=False)
    op.create_index(op.f("ix_clients_id"), "clients", ["id"], unique=False)

    op.create_table(
        "services",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("duration_minutes > 0", name=op.f("ck_services_duration_minutes_positive")),
        sa.CheckConstraint("price >= 0", name=op.f("ck_services_price_non_negative")),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_services_business_id_businesses"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_services")),
    )
    op.create_index("ix_services_business_id", "services", ["business_id"], unique=False)
    op.create_index("ix_services_is_active", "services", ["is_active"], unique=False)
    op.create_index(op.f("ix_services_id"), "services", ["id"], unique=False)

    op.create_table(
        "staff",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("specialization", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_staff_business_id_businesses"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_staff")),
    )
    op.create_index("ix_staff_business_id", "staff", ["business_id"], unique=False)
    op.create_index("ix_staff_is_active", "staff", ["is_active"], unique=False)
    op.create_index(op.f("ix_staff_id"), "staff", ["id"], unique=False)

    op.create_table(
        "working_hours",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("open_time", sa.Time(), nullable=True),
        sa.Column("close_time", sa.Time(), nullable=True),
        sa.Column("is_closed", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name=op.f("ck_working_hours_day_of_week_range")),
        sa.CheckConstraint(
            "is_closed = true OR (open_time IS NOT NULL AND close_time IS NOT NULL AND close_time > open_time)",
            name=op.f("ck_working_hours_open_close_valid_when_open"),
        ),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_working_hours_business_id_businesses"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_working_hours")),
        sa.UniqueConstraint("business_id", "day_of_week", name="uq_working_hours_business_day"),
    )
    op.create_index("ix_working_hours_business_id", "working_hours", ["business_id"], unique=False)
    op.create_index(op.f("ix_working_hours_id"), "working_hours", ["id"], unique=False)

    op.create_table(
        "ai_messages",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=True),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("ai_response", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(), nullable=True),
        sa.Column("action_taken", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_ai_messages_business_id_businesses"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], name=op.f("fk_ai_messages_client_id_clients"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_messages")),
    )
    op.create_index("ix_ai_messages_business_id", "ai_messages", ["business_id"], unique=False)
    op.create_index("ix_ai_messages_telegram_id", "ai_messages", ["telegram_id"], unique=False)
    op.create_index(op.f("ix_ai_messages_id"), "ai_messages", ["id"], unique=False)

    op.create_table(
        "staff_services",
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], name=op.f("fk_staff_services_service_id_services"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["staff_id"], ["staff.id"], name=op.f("fk_staff_services_staff_id_staff"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_staff_services")),
        sa.UniqueConstraint("staff_id", "service_id", name="uq_staff_services_staff_service"),
    )
    op.create_index("ix_staff_services_service_id", "staff_services", ["service_id"], unique=False)
    op.create_index("ix_staff_services_staff_id", "staff_services", ["staff_id"], unique=False)
    op.create_index(op.f("ix_staff_services_id"), "staff_services", ["id"], unique=False)

    op.create_table(
        "bookings",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("staff_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", booking_status, nullable=False),
        sa.Column("source", booking_source, nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("cancel_reason", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_bookings_business_id_businesses"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], name=op.f("fk_bookings_client_id_clients"), ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], name=op.f("fk_bookings_service_id_services"), ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["staff_id"], ["staff.id"], name=op.f("fk_bookings_staff_id_staff"), ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bookings")),
    )
    op.create_index("ix_bookings_business_id", "bookings", ["business_id"], unique=False)
    op.create_index("ix_bookings_client_id", "bookings", ["client_id"], unique=False)
    op.create_index("ix_bookings_service_id", "bookings", ["service_id"], unique=False)
    op.create_index("ix_bookings_staff_id", "bookings", ["staff_id"], unique=False)
    op.create_index("ix_bookings_start_time", "bookings", ["start_time"], unique=False)
    op.create_index("ix_bookings_status", "bookings", ["status"], unique=False)
    op.create_index(op.f("ix_bookings_id"), "bookings", ["id"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", notification_status, nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"], name=op.f("fk_notifications_booking_id_bookings"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_notifications_business_id_businesses"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], name=op.f("fk_notifications_client_id_clients"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notifications")),
    )
    op.create_index("ix_notifications_booking_id", "notifications", ["booking_id"], unique=False)
    op.create_index("ix_notifications_business_id", "notifications", ["business_id"], unique=False)
    op.create_index("ix_notifications_client_id", "notifications", ["client_id"], unique=False)
    op.create_index("ix_notifications_status", "notifications", ["status"], unique=False)
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)

    op.create_table(
        "subscriptions",
        sa.Column("business_id", sa.Integer(), nullable=False),
        sa.Column("plan", subscription_plan, nullable=False),
        sa.Column("status", subscription_status, nullable=False),
        sa.Column("bookings_limit", sa.Integer(), nullable=False),
        sa.Column("ai_messages_limit", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name=op.f("fk_subscriptions_business_id_businesses"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subscriptions")),
    )
    op.create_index("ix_subscriptions_business_id", "subscriptions", ["business_id"], unique=False)
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"], unique=False)
    op.create_index(op.f("ix_subscriptions_id"), "subscriptions", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_subscriptions_id"), table_name="subscriptions")
    op.drop_index("ix_subscriptions_status", table_name="subscriptions")
    op.drop_index("ix_subscriptions_business_id", table_name="subscriptions")
    op.drop_table("subscriptions")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_index("ix_notifications_status", table_name="notifications")
    op.drop_index("ix_notifications_client_id", table_name="notifications")
    op.drop_index("ix_notifications_business_id", table_name="notifications")
    op.drop_index("ix_notifications_booking_id", table_name="notifications")
    op.drop_table("notifications")
    op.drop_index(op.f("ix_bookings_id"), table_name="bookings")
    op.drop_index("ix_bookings_status", table_name="bookings")
    op.drop_index("ix_bookings_start_time", table_name="bookings")
    op.drop_index("ix_bookings_staff_id", table_name="bookings")
    op.drop_index("ix_bookings_service_id", table_name="bookings")
    op.drop_index("ix_bookings_client_id", table_name="bookings")
    op.drop_index("ix_bookings_business_id", table_name="bookings")
    op.drop_table("bookings")
    op.drop_index(op.f("ix_staff_services_id"), table_name="staff_services")
    op.drop_index("ix_staff_services_staff_id", table_name="staff_services")
    op.drop_index("ix_staff_services_service_id", table_name="staff_services")
    op.drop_table("staff_services")
    op.drop_index(op.f("ix_ai_messages_id"), table_name="ai_messages")
    op.drop_index("ix_ai_messages_telegram_id", table_name="ai_messages")
    op.drop_index("ix_ai_messages_business_id", table_name="ai_messages")
    op.drop_table("ai_messages")
    op.drop_index(op.f("ix_working_hours_id"), table_name="working_hours")
    op.drop_index("ix_working_hours_business_id", table_name="working_hours")
    op.drop_table("working_hours")
    op.drop_index(op.f("ix_staff_id"), table_name="staff")
    op.drop_index("ix_staff_is_active", table_name="staff")
    op.drop_index("ix_staff_business_id", table_name="staff")
    op.drop_table("staff")
    op.drop_index(op.f("ix_services_id"), table_name="services")
    op.drop_index("ix_services_is_active", table_name="services")
    op.drop_index("ix_services_business_id", table_name="services")
    op.drop_table("services")
    op.drop_index(op.f("ix_clients_id"), table_name="clients")
    op.drop_index("ix_clients_telegram_id", table_name="clients")
    op.drop_index("ix_clients_business_id", table_name="clients")
    op.drop_table("clients")
    op.drop_index(op.f("ix_businesses_id"), table_name="businesses")
    op.drop_index("ix_businesses_owner_id", table_name="businesses")
    op.drop_index("ix_businesses_is_active", table_name="businesses")
    op.drop_table("businesses")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    subscription_status.drop(op.get_bind(), checkfirst=True)
    subscription_plan.drop(op.get_bind(), checkfirst=True)
    notification_status.drop(op.get_bind(), checkfirst=True)
    booking_source.drop(op.get_bind(), checkfirst=True)
    booking_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
