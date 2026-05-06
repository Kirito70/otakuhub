"""Notification routes for Phase 11."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.notification import (
    NotificationListResponse,
    NotificationMarkReadRequest,
    NotificationMarkReadResponse,
    NotificationResponse,
)
from src.app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def get_notification_service(db: AsyncSession = Depends(get_db_session)) -> NotificationService:
    """Get NotificationService instance with request-scoped DB session."""
    return NotificationService(db)


@router.get("", response_model=NotificationListResponse)
async def get_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    notification_service: NotificationService = Depends(get_notification_service),
    user: User = Depends(get_current_user),
) -> NotificationListResponse:
    """Phase 11.5 — list current user's notifications."""
    items = await notification_service.get_user_notifications(
        user_id=user.id,
        limit=limit,
        offset=offset,
    )
    total = await notification_service.count_user_notifications(user_id=user.id)

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/read", response_model=NotificationMarkReadResponse)
async def mark_notifications_read(
    payload: NotificationMarkReadRequest,
    notification_service: NotificationService = Depends(get_notification_service),
    user: User = Depends(get_current_user),
) -> NotificationMarkReadResponse:
    """Phase 11.6 — mark current user's notifications as read."""
    updated_count = await notification_service.mark_notifications_as_read(
        user_id=user.id,
        notification_ids=payload.notification_ids,
    )
    return NotificationMarkReadResponse(updated_count=updated_count)
