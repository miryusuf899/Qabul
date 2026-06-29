from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, Notification, NotificationStatus


async def create_booking_notification(
    db: AsyncSession,
    booking: Booking,
    message: str,
    notification_type: str = "booking_confirmation",
) -> Notification:
    notification = Notification(
        business_id=booking.business_id,
        client_id=booking.client_id,
        booking_id=booking.id,
        type=notification_type,
        message=message,
        status=NotificationStatus.PENDING,
    )
    db.add(notification)
    await db.flush()
    return notification
