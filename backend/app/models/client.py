from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.mixins import IdMixin


class Client(IdMixin, TimestampMixin, Base):
    __tablename__ = "clients"
    __table_args__ = (UniqueConstraint("business_id", "telegram_id", name="uq_clients_business_telegram"),)

    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    telegram_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    total_visits: Mapped[int] = mapped_column(nullable=False, default=0)
    last_visit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    business = relationship("Business", back_populates="clients")
    bookings = relationship("Booking", back_populates="client")
    ai_messages = relationship("AIMessage", back_populates="client")
    notifications = relationship("Notification", back_populates="client")


Index("ix_clients_business_id", Client.business_id)
Index("ix_clients_telegram_id", Client.telegram_id)
