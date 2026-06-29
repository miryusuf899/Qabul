"""SQLAlchemy models are imported here for Alembic autogeneration."""

from app.models.ai_message import AIMessage
from app.models.booking import Booking
from app.models.business import Business
from app.models.client import Client
from app.models.enums import (
    BookingSource,
    BookingStatus,
    NotificationStatus,
    SubscriptionPlan,
    SubscriptionStatus,
    UserRole,
)
from app.models.notification import Notification
from app.models.service import Service
from app.models.staff import Staff, StaffService
from app.models.subscription import Subscription
from app.models.user import User
from app.models.working_hour import WorkingHour

__all__ = [
    "AIMessage",
    "Booking",
    "BookingSource",
    "BookingStatus",
    "Business",
    "Client",
    "Notification",
    "NotificationStatus",
    "Service",
    "Staff",
    "StaffService",
    "Subscription",
    "SubscriptionPlan",
    "SubscriptionStatus",
    "User",
    "UserRole",
    "WorkingHour",
]
