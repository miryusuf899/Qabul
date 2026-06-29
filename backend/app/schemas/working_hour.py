from __future__ import annotations

from datetime import time

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkingHourUpsert(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    open_time: time | None = None
    close_time: time | None = None
    is_closed: bool = False

    @model_validator(mode="after")
    def validate_hours(self) -> "WorkingHourUpsert":
        if self.is_closed:
            return self
        if self.open_time is None or self.close_time is None:
            raise ValueError("open_time and close_time are required when day is open")
        if self.close_time <= self.open_time:
            raise ValueError("close_time must be greater than open_time")
        return self


class WorkingHourRead(BaseModel):
    id: int
    business_id: int
    day_of_week: int
    open_time: time | None
    close_time: time | None
    is_closed: bool

    model_config = ConfigDict(from_attributes=True)
