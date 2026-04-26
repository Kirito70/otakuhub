"""API routes for user list management."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID

from src.app.services.tracking_service import TrackingService
from src.app.services.user_service import UserService
from src.app.schemas.tracking import ListEntryCreate, ListEntryUpdate, ListEntryResponse
from src.app.core.auth import get_current_user
from src.app.models import User

router = APIRouter(prefix="/lists", tags=["lists"])

# Dependency injection for tracking service
def get_tracking_service():
    """Get TrackingService instance."""
    return TrackingService()

# Dependency injection for user service (only needed for auth)
def get_user_service():
    """Get UserService instance."""
    return UserService()

@router.get("/entries/{entry_id}", response_model=ListEntryResponse)
async def get_list_entry(
    entry_id: UUID,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user)
):
    """Get a specific list entry."""
    entry = await tracking_service.get_user_list_entry(user.id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="List entry not found")
    return entry

@router.get("/entries")
async def get_user_list(
    status: Optional[str] = None,
    media_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user)
):
    """Get user's list entries."""
    entries = await tracking_service.get_user_list(
        user_id=user.id,
        status=status,
        media_type=media_type,
        limit=limit,
        offset=offset
    )
    return {
        "items": entries,
        "total": len(entries),
        "limit": limit,
        "offset": offset
    }

@router.post("/entries", response_model=ListEntryResponse)
async def create_list_entry(
    entry_create: ListEntryCreate,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user)
):
    """Create a new list entry."""
    entry = await tracking_service.create_list_entry(entry_create)
    return entry

@router.put("/entries/{entry_id}", response_model=ListEntryResponse)
async def update_list_entry(
    entry_id: UUID,
    entry_update: ListEntryUpdate,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user)
):
    """Update a list entry."""
    entry = await tracking_service.update_list_entry(entry_id, entry_update)
    if not entry:
        raise HTTPException(status_code=404, detail="List entry not found")
    return entry

@router.delete("/entries/{entry_id}")
async def delete_list_entry(
    entry_id: UUID,
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user)
):
    """Delete a list entry (soft delete)."""
    success = await tracking_service.delete_list_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="List entry not found")
    return {"message": "Entry deleted successfully"}

@router.get("/statistics")
async def get_user_statistics(
    tracking_service: TrackingService = Depends(get_tracking_service),
    user: User = Depends(get_current_user)
):
    """Get user's tracking statistics."""
    stats = await tracking_service.get_user_statistics(user.id)
    return stats