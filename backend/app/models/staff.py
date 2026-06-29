from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, TimestampMixin
from app.models.mixins import IdMixin


class Staff(IdMixin, TimestampMixin, Base):
    __tablename__ = "staff"

    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    business = relationship("Business", back_populates="staff_members")
    service_links = relationship("StaffService", back_populates="staff", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="staff")


class StaffService(IdMixin, Base):
    __tablename__ = "staff_services"
    __table_args__ = (UniqueConstraint("staff_id", "service_id", name="uq_staff_services_staff_service"),)

    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)

    staff = relationship("Staff", back_populates="service_links")
    service = relationship("Service", back_populates="staff_links")


Index("ix_staff_business_id", Staff.business_id)
Index("ix_staff_is_active", Staff.is_active)
Index("ix_staff_services_staff_id", StaffService.staff_id)
Index("ix_staff_services_service_id", StaffService.service_id)
