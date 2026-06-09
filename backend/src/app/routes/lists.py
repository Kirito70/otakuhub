"""API routes for user list management."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.tracking import (
    CustomListCreate,
    CustomListEntriesReplaceRequest,
    CustomListEntriesReplaceResponse,
    CustomListResponse,
    ListEntryCreate,
    ListEntryHistoryResponse,
    ListEntryResponse,
    ListEntryUpdate,
    UserListHistoryResponse,
    UserListResponse,
)
from src.app.services.tracking_service import TrackingService

router = APIRouter(prefix="/lists", tags=["lists"])


def get_tracking_service(db: AsyncSession = Depends(get_db_session)) -> TrackingService:
    """Get TrackingService instance with request-scoped DB session."""
    return TrackingService(db)


@router.get("/me", response_model=UserListResponse)
async def get_my_list(
    status: Optional[str] = Query(default=None, description="Single status filter (legacy)"),
    statuses: Optional[str] = Query(default=None, description="Comma-separated status list (e.g. 'watching,reading')"),
    media_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> UserListResponse:
    """Phase 6.1 — get the authenticated user's full tracking list."""
    entries = await tracking_service.get_user_list(
        user_id=user.id,
        status=status,
        statuses=statuses,
        media_type=media_type,
        limit=limit,
        offset=offset,
    )
    return UserListResponse(
        items=[ListEntryResponse.model_validate(entry) for entry in entries],
        total=len(entries),
        limit=limit,
        offset=offset,
    )


@router.get("/entries/{media_id}", response_model=ListEntryResponse)
async def get_list_entry(
    media_id: UUID,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> ListEntryResponse:
    """Get a specific list entry by media ID for current user."""
    entry = await tracking_service.get_user_list_entry(user.id, media_id)
    if not entry:
        raise HTTPException(status_code=404, detail="List entry not found")
    # Use model_dump to avoid lazy-loading media relationship
    data = entry.model_dump()
    return ListEntryResponse(**data)


@router.post("", response_model=ListEntryResponse, status_code=201)
async def create_list_entry_root(
    entry_create: ListEntryCreate,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> ListEntryResponse:
    """Phase 6.2 — add an item to the authenticated user's list."""
    try:
        entry = await tracking_service.create_list_entry(user.id, entry_create)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    # Use model_dump to avoid lazy-loading media relationship
    data = entry.model_dump()
    return ListEntryResponse(**data)


@router.post("/entries", response_model=ListEntryResponse, status_code=201)
async def create_list_entry(
    entry_create: ListEntryCreate,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> ListEntryResponse:
    """Backward-compatible create endpoint."""
    return await create_list_entry_root(entry_create, tracking_service, user)


@router.patch("/{media_id}", response_model=ListEntryResponse)
async def update_list_entry_root(
    media_id: UUID,
    entry_update: ListEntryUpdate,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> ListEntryResponse:
    """Phase 6.3 — update status/progress/score for a list entry."""
    entry = await tracking_service.update_list_entry(user.id, media_id, entry_update)
    if not entry:
        raise HTTPException(status_code=404, detail="List entry not found")
    # Use model_dump to avoid lazy-loading media relationship
    data = entry.model_dump()
    return ListEntryResponse(**data)


@router.patch("/entries/{media_id}", response_model=ListEntryResponse)
async def update_list_entry(
    media_id: UUID,
    entry_update: ListEntryUpdate,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> ListEntryResponse:
    """Backward-compatible update endpoint."""
    return await update_list_entry_root(media_id, entry_update, tracking_service, user)


@router.delete("/{media_id}")
async def delete_list_entry_root(
    media_id: UUID,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Phase 6.4 — soft delete a list entry by media ID."""
    success = await tracking_service.delete_list_entry(user.id, media_id)
    if not success:
        raise HTTPException(status_code=404, detail="List entry not found")
    return {"message": "Entry deleted successfully"}


@router.delete("/entries/{media_id}")
async def delete_list_entry(
    media_id: UUID,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Backward-compatible delete endpoint."""
    return await delete_list_entry_root(media_id, tracking_service, user)


@router.get("/me/history", response_model=UserListHistoryResponse)
async def get_my_list_history(
    limit: int = Query(default=50, ge=1, le=200),
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> UserListHistoryResponse:
    """Phase 6.5 — get activity history for authenticated user's list."""
    history = await tracking_service.get_user_activity_feed(user.id, limit=limit)
    return UserListHistoryResponse(
        items=[ListEntryHistoryResponse.model_validate(item) for item in history],
        total=len(history),
        limit=limit,
    )


@router.post("/custom", response_model=CustomListResponse, status_code=201)
async def create_custom_list(
    payload: CustomListCreate,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> CustomListResponse:
    """Phase 6.8 — create a custom list for the authenticated user."""
    custom_list = await tracking_service.create_custom_list(user.id, payload)
    return CustomListResponse.model_validate(custom_list)


@router.put("/custom/{list_id}/entries", response_model=CustomListEntriesReplaceResponse)
async def replace_custom_list_entries(
    list_id: UUID,
    payload: CustomListEntriesReplaceRequest,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> CustomListEntriesReplaceResponse:
    """Phase 6.9 — replace all entries for a custom list."""
    total = await tracking_service.replace_custom_list_entries(user.id, list_id, payload)
    if total is None:
        raise HTTPException(status_code=404, detail="Custom list not found")
    return CustomListEntriesReplaceResponse(list_id=list_id, total_entries=total)


@router.get("/statistics")
async def get_user_statistics(
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user),
) -> dict:
    """Get user's tracking statistics."""
    return await tracking_service.get_user_statistics(user.id)
