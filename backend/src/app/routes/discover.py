"""API routes for home, global search, and calendar (F11.11)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.services.media_service import MediaService
from src.app.schemas.home import HomeData
from src.app.schemas.search import SearchResponse
from src.app.schemas.calendar import CalendarResponse

router = APIRouter()


def get_media_service() -> MediaService:
    """Get MediaService instance."""
    return MediaService()


# ---------------------------------------------------------------------------
# GET /home — Composite home payload
# ---------------------------------------------------------------------------


@router.get("/home", response_model=HomeData)
async def get_home(
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user),
) -> HomeData:
    """Get the composite home page payload.

    Returns 6 sections:
      - spotlight: top trending media (hero banner)
      - continue_watching: user's in-progress items
      - friend_recommendations: recommendations from group members
      - group_watching_now: what friends are watching together
      - airing_soon: upcoming episode airings
      - trending_in_group: popular media among group members
    """
    return await media_service.get_home_data(user_id=user.id)


# ---------------------------------------------------------------------------
# GET /search — Grouped global search
# ---------------------------------------------------------------------------


@router.get("/search", response_model=SearchResponse)
async def global_search(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(default=5, ge=1, le=20, description="Results per media type"),
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user),
) -> SearchResponse:
    """Global search across all media types grouped by type.

    Returns results grouped into anime, manga, manhwa, and light_novel
    sections, each with a limited preview and total count.
    """
    return await media_service.grouped_search(query_text=q, limit_per_type=limit)


# ---------------------------------------------------------------------------
# GET /calendar — Unified episode + chapter calendar
# ---------------------------------------------------------------------------


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    type: Optional[str] = Query(default=None, description="Media type filter"),
    start_date: Optional[str] = Query(default=None, description="Start date (ISO format). Defaults to today."),
    end_date: Optional[str] = Query(default=None, description="End date (ISO format). Defaults to 1 year from now."),
    limit: int = Query(default=100, ge=1, le=500, description="Max events to return"),
    media_service: MediaService = Depends(get_media_service),
    user: User = Depends(get_current_user),
) -> CalendarResponse:
    """Get a unified calendar of upcoming episode airings and chapter releases.

    Merges episodes (from the episodes table) and chapters (from the chapters
    table) into a single sorted list of CalendarEvent items.

    Supports optional media_type filter and date range.
    """
    parsed_start: Optional[datetime] = None
    parsed_end: Optional[datetime] = None
    if start_date:
        parsed_start = datetime.fromisoformat(start_date)
    if end_date:
        parsed_end = datetime.fromisoformat(end_date)

    return await media_service.get_calendar(
        start_date=parsed_start,
        end_date=parsed_end,
        media_type=type,
        limit=limit,
    )
