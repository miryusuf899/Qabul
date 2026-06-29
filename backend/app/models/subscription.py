from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import SubscriptionPlan, SubscriptionStatus
from app.models.mixins import IdMixin


class Subscription(IdMixin, Base):
    __tablename__ = "subscriptions"

    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    plan: Mapped[SubscriptionPlan] = mapped_column(
        Enum(SubscriptionPlan, name="subscription_plan", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=SubscriptionPlan.FREE,
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        Enum(
            SubscriptionStatus,
            name="subscription_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=SubscriptionStatus.ACTIVE,
    )
    bookings_limit: Mapped[int] = mapped_column(nullable=False, default=100)
    ai_messages_limit: Mapped[int] = mapped_column(nullable=False, default=500)
    starts_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    business = relationship("Business", back_populates="subscriptions")


Index("ix_subscriptions_business_id", Subscription.business_id)
Index("ix_subscriptions_status", Subscription.status)
