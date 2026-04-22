"""
Lists and tracking routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

router = APIRouter(prefix="/lists", tags=["lists"])

@router.get("/me")
async def get_user_list():
    """Get current user's list."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/")
async def add_to_list():
    """Add media to user's list."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.patch("/{media_id}")
async def update_list_entry():
    """Update list entry."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.delete("/{media_id}")
async def remove_from_list():
    """Remove media from user's list."""
    raise HTTPException(status_code=501, detail="Not implemented")