"""Watch party routes for Phase 10."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.watchparty import WatchPartyCreateRequest, WatchPartyDetailResponse, WatchPartyListResponse, WatchPartyResponse
from src.app.schemas.watchparty import WatchPartyRsvpListResponse, WatchPartyRsvpRequest, WatchPartyRsvpResponse, WatchPartyUpdateRequest
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


@router.get("", response_model=WatchPartyListResponse)
async def get_upcoming_watch_parties(
    group_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> WatchPartyListResponse:
    """Phase 10.2 — list upcoming parties in user's groups."""
    try:
        items = await watchparty_service.get_upcoming_watch_parties_for_user(
            user_id=user.id,
            group_id=group_id,
            limit=limit,
            offset=offset,
        )
        total = await watchparty_service.count_upcoming_watch_parties_for_user(
            user_id=user.id,
            group_id=group_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return WatchPartyListResponse(
        items=[WatchPartyResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/past", response_model=WatchPartyListResponse)
async def get_past_watch_parties(
    group_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> WatchPartyListResponse:
    """Phase 10.4 — list past/completed/cancelled parties in user's groups."""
    try:
        items = await watchparty_service.get_past_watch_parties_for_user(
            user_id=user.id,
            group_id=group_id,
            limit=limit,
            offset=offset,
        )
        total = await watchparty_service.count_past_watch_parties_for_user(
            user_id=user.id,
            group_id=group_id,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return WatchPartyListResponse(
        items=[WatchPartyResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{party_id}", response_model=WatchPartyResponse)
async def update_watch_party(
    party_id: UUID,
    payload: WatchPartyUpdateRequest,
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> WatchPartyResponse:
    """Update a watch party. Only the host can update."""
    updates = payload.model_dump(exclude_unset=True)
    party = await watchparty_service.update_watch_party(party_id, updates, user_id=user.id)
    if party is None:
        existing = await watchparty_service.get_watch_party(party_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Watch party not found")
        raise HTTPException(status_code=403, detail="Only the host can update the watch party")
    return WatchPartyResponse.model_validate(party)


@router.delete("/{party_id}", status_code=204)
async def delete_watch_party(
    party_id: UUID,
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> None:
    """Soft-delete a watch party. Only the host can delete."""
    deleted = await watchparty_service.delete_watch_party(party_id, user_id=user.id)
    if not deleted:
        existing = await watchparty_service.get_watch_party(party_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Watch party not found")
        raise HTTPException(status_code=403, detail="Only the host can delete the watch party")


@router.get("/{party_id}/rsvps", response_model=WatchPartyRsvpListResponse)
async def get_watch_party_rsvps(
    party_id: UUID,
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> WatchPartyRsvpListResponse:
    """Get all RSVPs for a watch party (group-membership checked)."""
    try:
        detail = await watchparty_service.get_watch_party_detail(
            party_id=party_id,
            user_id=user.id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    rsvps = await watchparty_service.get_rsvps_for_party(party_id)
    items = [WatchPartyRsvpResponse.model_validate(r) for r in rsvps]
    return WatchPartyRsvpListResponse(items=items, total=len(items))


@router.get("/{party_id}", response_model=WatchPartyDetailResponse)
async def get_watch_party_detail(
    party_id: UUID,
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> WatchPartyDetailResponse:
    """Phase 10.3 — get single watch party detail with RSVP summary."""
    try:
        detail = await watchparty_service.get_watch_party_detail(
            party_id=party_id,
            user_id=user.id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return WatchPartyDetailResponse(**detail)


@router.post("/{party_id}/rsvp", response_model=WatchPartyRsvpResponse)
async def rsvp_watch_party(
    party_id: UUID,
    payload: WatchPartyRsvpRequest,
    watchparty_service: WatchPartyService = Depends(get_watch_party_service),
    user: User = Depends(get_current_user),
) -> WatchPartyRsvpResponse:
    """Phase 10.3 — RSVP to a watch party."""
    try:
        rsvp = await watchparty_service.rsvp_to_watch_party_for_group_member(
            party_id=party_id,
            user_id=user.id,
            status=payload.status.value,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return WatchPartyRsvpResponse.model_validate(rsvp)
