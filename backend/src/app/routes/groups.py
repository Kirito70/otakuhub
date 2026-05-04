"""Group management routes for Phase 5."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models.group import Group
from src.app.models.group_member import GroupMember
from src.app.models.user import User
from src.app.schemas.group import GroupCreate, GroupDetail
from src.app.services.group_service import group_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post("", response_model=GroupDetail, status_code=201)
async def create_group(
    payload: GroupCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> GroupDetail:
    group = await group_service.create_group(db, current_user, payload)
    return await _to_group_detail(db, group)


@router.get("/{group_id}", response_model=GroupDetail)
async def get_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> GroupDetail:
    group = await group_service.get_group_for_user(db, group_id, current_user)
    return await _to_group_detail(db, group)


@router.post("/join/{invite_code}")
async def join_group(
    invite_code: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    member = await group_service.join_by_invite(db, invite_code, current_user)
    return {
        "group_id": str(member.group_id),
        "user_id": str(member.user_id),
        "role": member.role,
        "joined_at": member.joined_at.isoformat(),
    }


@router.get("/{group_id}/members")
async def get_group_members(
    group_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    members = await group_service.list_members(db, group_id, current_user)
    return {"items": members, "total": len(members)}


async def _to_group_detail(db: AsyncSession, group: Group) -> GroupDetail:
    count_stmt = select(GroupMember).where(GroupMember.group_id == group.id)
    member_count = len((await db.execute(count_stmt)).scalars().all())
    return GroupDetail(
        id=group.id,
        name=group.name,
        is_private=group.is_private,
        owner_id=group.owner_id,
        avatar_url=group.avatar_url,
        created_at=group.created_at,
        invite_code=group.invite_code,
        member_count=member_count,
        description=group.description,
        updated_at=group.updated_at,
    )
