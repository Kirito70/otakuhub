"""Social routes for Phase 9."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models import User
from src.app.schemas.social import (
    RecommendationCreateRequest,
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
