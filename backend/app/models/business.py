from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.mixins import IdMixin


class Business(IdMixin, TimestampMixin, Base):
    __tablename__ = "businesses"

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    business_type: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Dushanbe")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    ai_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    owner = relationship("User", back_populates="businesses")
    services = relationship("Service", back_populates="business", cascade="all, delete-orphan")
    staff_members = relationship("Staff", back_populates="business", cascade="all, delete-orphan")
    working_hours = relationship("WorkingHour", back_populates="business", cascade="all, delete-orphan")
    clients = relationship("Client", back_populates="business", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="business", cascade="all, delete-orphan")
    ai_messages = relationship("AIMessage", back_populates="business", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="business", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="business", cascade="all, delete-orphan")


Index("ix_businesses_owner_id", Business.owner_id)
Index("ix_businesses_is_active", Business.is_active)
