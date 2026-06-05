"""Group management routes for Phase 5."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

from src.app.core.auth import get_current_user
from src.app.database import get_db_session
from src.app.models.group import Group
from src.app.models.group_member import GroupMember
from src.app.models.user import User
from src.app.schemas.group import GroupCreate, GroupDetail, GroupSummary, GroupUpdate
from src.app.services.group_service import group_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=dict)
async def list_groups(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """List all groups the current user belongs to."""
    groups = await group_service.list_user_groups(db, current_user)
    items = []
    for g in groups:
        count_stmt = select(GroupMember).where(GroupMember.group_id == g.id)
        member_count = len((await db.execute(count_stmt)).scalars().all())
        items.append(
            GroupSummary(
                id=g.id,
                name=g.name,
                is_private=g.is_private,
                owner_id=g.owner_id,
                avatar_url=g.avatar_url,
                created_at=g.created_at,
            )
        )
    return {"items": items, "total": len(items)}


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


@router.patch("/{group_id}", response_model=GroupDetail)
async def update_group(
    group_id: UUID,
    payload: GroupUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> GroupDetail:
    """Update a group's name, description, or privacy setting."""
    group = await group_service.update_group(db, group_id, current_user, payload)
    return await _to_group_detail(db, group)


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """Soft-delete a group. Only the owner can delete."""
    await group_service.delete_group(db, group_id, current_user)


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


@router.delete("/{group_id}/members/{user_id}", status_code=204)
async def remove_group_member(
    group_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """Remove a member from a group. Owner or admin can remove members."""
    await group_service.remove_member(db, group_id, user_id, current_user)


@router.patch("/{group_id}/members/{user_id}/role")
async def change_member_role(
    group_id: UUID,
    user_id: UUID,
    body: dict,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Change a member's role. Only the owner can change roles."""
    new_role = body.get("role", "")
    result = await group_service.change_member_role(
        db, group_id, user_id, new_role, current_user
    )
    return result


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
