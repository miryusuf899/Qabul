from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.enums import BookingSource, BookingStatus
from app.models.mixins import IdMixin


class Booking(IdMixin, TimestampMixin, Base):
    __tablename__ = "bookings"

    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id", ondelete="RESTRICT"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=BookingStatus.CONFIRMED,
    )
    source: Mapped[BookingSource] = mapped_column(
        Enum(BookingSource, name="booking_source", values_callable=lambda enum: [item.value for item in enum]),
        nullable=False,
        default=BookingSource.DASHBOARD,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    business = relationship("Business", back_populates="bookings")
    client = relationship("Client", back_populates="bookings")
    staff = relationship("Staff", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
    notifications = relationship("Notification", back_populates="booking")


Index("ix_bookings_business_id", Booking.business_id)
Index("ix_bookings_client_id", Booking.client_id)
Index("ix_bookings_staff_id", Booking.staff_id)
Index("ix_bookings_service_id", Booking.service_id)
Index("ix_bookings_start_time", Booking.start_time)
Index("ix_bookings_status", Booking.status)
