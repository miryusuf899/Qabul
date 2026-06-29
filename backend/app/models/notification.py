from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import NotificationStatus
from app.models.mixins import IdMixin


class Notification(IdMixin, Base):
    __tablename__ = "notifications"

    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id", ondelete="SET NULL"), nullable=True)
    type: Mapped[str] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=NotificationStatus.PENDING,
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    business = relationship("Business", back_populates="notifications")
    client = relationship("Client", back_populates="notifications")
    booking = relationship("Booking", back_populates="notifications")


Index("ix_notifications_business_id", Notification.business_id)
Index("ix_notifications_client_id", Notification.client_id)
Index("ix_notifications_booking_id", Notification.booking_id)
Index("ix_notifications_status", Notification.status)
