"""Group service for Phase 5 group management."""

from __future__ import annotations

from datetime import datetime
from secrets import token_hex
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.models.group import Group
from src.app.models.group_member import GroupMember
from src.app.models.user import User
from src.app.schemas.group import GroupCreate, GroupDetail


class GroupService:
    """Business logic for group operations."""

    async def create_group(self, db: AsyncSession, owner: User, payload: GroupCreate) -> Group:
        group = Group(
            name=payload.name,
            description=payload.description,
            invite_code=token_hex(12),
            owner_id=owner.id,
            is_private=payload.is_private,
        )
        db.add(group)
        await db.flush()

        owner_membership = GroupMember(group_id=group.id, user_id=owner.id, role="owner")
        db.add(owner_membership)
        await db.commit()
        await db.refresh(group)
        return group

    async def get_group_for_user(self, db: AsyncSession, group_id: UUID, user: User) -> Group:
        group_stmt = select(Group).where(Group.id == group_id, Group.deleted_at.is_(None))
        group = (await db.execute(group_stmt)).scalar_one_or_none()
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        member_stmt = select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user.id)
        member = (await db.execute(member_stmt)).scalar_one_or_none()
        if member is None:
            raise HTTPException(status_code=403, detail="Forbidden")

        return group

    async def join_by_invite(self, db: AsyncSession, invite_code: str, user: User) -> GroupMember:
        group_stmt = select(Group).where(Group.invite_code == invite_code, Group.deleted_at.is_(None))
        group = (await db.execute(group_stmt)).scalar_one_or_none()
        if group is None:
            raise HTTPException(status_code=404, detail="Invite code not found")

        existing_stmt = select(GroupMember).where(GroupMember.group_id == group.id, GroupMember.user_id == user.id)
        existing = (await db.execute(existing_stmt)).scalar_one_or_none()
        if existing:
            return existing

        member = GroupMember(group_id=group.id, user_id=user.id, role="member")
        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member

    async def list_members(self, db: AsyncSession, group_id: UUID, user: User) -> list[dict[str, Any]]:
        await self.get_group_for_user(db, group_id, user)

        stmt = (
            select(User, GroupMember)
            .join(GroupMember, GroupMember.user_id == User.id)
            .where(GroupMember.group_id == group_id)
        )
        rows = (await db.execute(stmt)).all()

        result: list[dict[str, Any]] = []
        for row in rows:
            u, gm = row
            result.append(
                {
                    "id": str(u.id),
                    "username": u.username,
                    "display_name": u.display_name,
                    "avatar_url": u.avatar_url,
                    "role": gm.role,
                    "joined_at": gm.joined_at.isoformat(),
                }
            )
        return result


group_service = GroupService()
