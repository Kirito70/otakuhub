"""
Media routes for anime/manga.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db

router = APIRouter(prefix="/media", tags=["media"])

@router.get("/")
async def search_media():
    """Search media endpoint."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{id}")
async def get_media():
    """Get media details by ID."""
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/airing")
async def get_airing_schedule():
    """Get airing schedule."""
    raise HTTPException(status_code=501, detail="Not implemented")