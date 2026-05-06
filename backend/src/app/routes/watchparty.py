"""Watch party routes for Phase 10."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.watchparty import WatchPartyCreateRequest, WatchPartyResponse
from src.app.services.watch_party_service import WatchPartyService

router = APIRouter(prefix="/watchparty", tags=["watchparty"])


def get_watch_party_service(db: AsyncSession = Depends(get_db_session)) -> WatchPartyService:
    """Get WatchPartyService instance with request-scoped DB session."""
    return WatchPartyService(db)


@router.post("", response_model=WatchPartyResponse, status_code=201)
async def create_watch_party(
    payload: WatchPartyCreateRequest,
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> WatchPartyResponse:
    """Phase 10.1 — create watch party in a group."""
    try:
        party = await watchparty_service.create_watch_party_for_group_member(
            host_user_id=user.id,
            group_id=payload.group_id,
            media_id=payload.media_id,
            scheduled_at=payload.scheduled_at,
            title=payload.title,
            episode_number=payload.episode_number,
            stream_url=payload.stream_url,
            sync_url=payload.sync_url,
            notes=payload.notes,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return WatchPartyResponse.model_validate(party)
