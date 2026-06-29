from __future__ import annotations

from datetime import time

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Index, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import IdMixin


class WorkingHour(IdMixin, Base):
    __tablename__ = "working_hours"
    __table_args__ = (
        UniqueConstraint("business_id", "day_of_week", name="uq_working_hours_business_day"),
        CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="day_of_week_range"),
        CheckConstraint(
            "is_closed = true OR (open_time IS NOT NULL AND close_time IS NOT NULL AND close_time > open_time)",
            name="open_close_valid_when_open",
        ),
    )

    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(nullable=False)
    open_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    close_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    business = relationship("Business", back_populates="working_hours")


Index("ix_working_hours_business_id", WorkingHour.business_id)
