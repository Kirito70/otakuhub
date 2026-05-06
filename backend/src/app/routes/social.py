"""Social routes for Phase 9."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.social import (
    DiscussionCreateRequest,
    DiscussionListResponse,
    DiscussionReplyCreateRequest,
    DiscussionReplyResponse,
    DiscussionResponse,
    RecommendationCreateRequest,
    RecommendationInboxResponse,
    RecommendationResponse,
    SocialFeedItemResponse,
    SocialFeedResponse,
)
from src.app.services.social_service import SocialService

router = APIRouter(prefix="/social", tags=["social"])


def get_social_service(db: AsyncSession = Depends(get_db_session)) -> SocialService:
    """Get SocialService instance with request-scoped DB session."""
    return SocialService(db)


@router.get("/feed", response_model=SocialFeedResponse)
async def get_social_feed(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    social_service: SocialService = Depends(get_social_service),
    user: User = Depends(get_current_user),
) -> SocialFeedResponse:
    """Phase 9.1 — group activity feed from shared-group members."""
    items = await social_service.get_group_activity_feed(user_id=user.id, limit=limit, offset=offset)
    total = await social_service.count_group_activity_feed(user_id=user.id)

    return SocialFeedResponse(
        items=[SocialFeedItemResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/recommend", response_model=RecommendationResponse, status_code=201)
async def create_recommendation(
    payload: RecommendationCreateRequest,
    social_service: SocialService = Depends(get_social_service),
    user: User = Depends(get_current_user),
) -> RecommendationResponse:
    """Phase 9.2 — recommend a media title to a shared-group member."""
    try:
        recommendation = await social_service.create_recommendation_for_shared_group(
            from_user_id=user.id,
            to_user_id=payload.to_user_id,
            media_id=payload.media_id,
            message=payload.message,
        )
    except ValueError as exc:
        detail = str(exc)
        status_code = 400
        if "not found" in detail.lower():
            status_code = 404
        elif "already exists" in detail.lower():
            status_code = 409
        raise HTTPException(status_code=status_code, detail=detail) from exc

    return RecommendationResponse.model_validate(recommendation)


@router.get("/recommendations/inbox", response_model=RecommendationInboxResponse)
async def get_recommendation_inbox(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    include_acknowledged: bool = Query(default=True),
    social_service: SocialService = Depends(get_social_service),
    user: User = Depends(get_current_user),
) -> RecommendationInboxResponse:
    """Phase 9.3 — current user's recommendation inbox."""
    items = await social_service.get_user_recommendations_inbox(
        user_id=user.id,
        limit=limit,
        offset=offset,
        include_acknowledged=include_acknowledged,
    )
    total = await social_service.count_user_recommendations_inbox(
        user_id=user.id,
        include_acknowledged=include_acknowledged,
    )

    return RecommendationInboxResponse(
        items=[RecommendationResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/recommendations/{recommendation_id}/acknowledge", response_model=RecommendationResponse)
async def acknowledge_recommendation(
    recommendation_id: UUID,
    social_service: SocialService = Depends(get_social_service),
    user: User = Depends(get_current_user),
) -> RecommendationResponse:
    """Phase 9.4 — acknowledge a recommendation in current user's inbox."""
    updated = await social_service.acknowledge_recommendation(
        recommendation_id=recommendation_id,
        user_id=user.id,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return RecommendationResponse.model_validate(updated)


@router.post("/discussions", response_model=DiscussionResponse, status_code=201)
async def create_discussion(
    payload: DiscussionCreateRequest,
    social_service: SocialService = Depends(get_social_service),
    user: User = Depends(get_current_user),
) -> DiscussionResponse:
    """Phase 9.5 — create discussion in a group thread."""
    try:
        discussion = await social_service.create_discussion_for_group_member(
            user_id=user.id,
            media_id=payload.media_id,
            group_id=payload.group_id,
            title=payload.title,
            body=payload.body,
            has_spoilers=payload.has_spoilers,
            episode_number=payload.episode_number,
            chapter_number=payload.chapter_number,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return DiscussionResponse.model_validate(discussion)


@router.get("/discussions/{media_id}", response_model=DiscussionListResponse)
async def get_discussions_for_media(
    media_id: UUID,
    group_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    social_service: SocialService = Depends(get_social_service),
    user: User = Depends(get_current_user),
) -> DiscussionListResponse:
    """Phase 9.6 — list discussions visible to current user for media."""
    items = await social_service.get_discussions_for_user_media(
        user_id=user.id,
        media_id=media_id,
        group_id=group_id,
        limit=limit,
        offset=offset,
    )
    total = await social_service.count_discussions_for_user_media(
        user_id=user.id,
        media_id=media_id,
        group_id=group_id,
    )

    return DiscussionListResponse(
        items=[DiscussionResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/discussions/{discussion_id}/replies", response_model=DiscussionReplyResponse, status_code=201)
async def create_discussion_reply(
    discussion_id: UUID,
    payload: DiscussionReplyCreateRequest,
    social_service: SocialService = Depends(get_social_service),
    user: User = Depends(get_current_user),
) -> DiscussionReplyResponse:
    """Phase 9.7 — create reply under a discussion."""
    try:
        reply = await social_service.create_discussion_reply_for_group_member(
            user_id=user.id,
            discussion_id=discussion_id,
            body=payload.body,
            has_spoilers=payload.has_spoilers,
            parent_reply_id=payload.parent_reply_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    return DiscussionReplyResponse.model_validate(reply)
