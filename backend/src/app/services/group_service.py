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
from src.app.repositories.group_repository import GroupRepository
from src.app.repositories.group_member_repository import GroupMemberRepository
from src.app.schemas.group import GroupCreate, GroupDetail, GroupUpdate


class GroupService:
    """Business logic for group operations."""

    # ── Repository helpers ───────────────────────────────────────────────

    def _group_repo(self, db: AsyncSession) -> GroupRepository:
        """Get a GroupRepository bound to the given session."""
        return GroupRepository(db)

    def _member_repo(self, db: AsyncSession) -> GroupMemberRepository:
        """Get a GroupMemberRepository bound to the given session."""
        return GroupMemberRepository(db)

    # ── Public methods ────────────────────────────────────────────────────

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
        group = await self._group_repo(db).get_by_id(group_id)
        if group is None:
            raise HTTPException(status_code=404, detail="Group not found")

        is_member = await self._member_repo(db).is_member(group_id, user.id)
        if not is_member:
            raise HTTPException(status_code=403, detail="Forbidden")

        return group

    async def join_by_invite(self, db: AsyncSession, invite_code: str, user: User) -> GroupMember:
        group = await self._group_repo(db).get_by_invite_code(invite_code)
        if group is None:
            raise HTTPException(status_code=404, detail="Invite code not found")

        is_member = await self._member_repo(db).is_member(group.id, user.id)
        if is_member:
            # Re-fetch the existing membership to return
            members = await self._member_repo(db).list_by_user(user.id)
            for m in members:
                if m.group_id == group.id:
                    return m

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

    async def list_user_groups(self, db: AsyncSession, user: User) -> list[Group]:
        """List all groups the user is a member of."""
        stmt = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.user_id == user.id, Group.deleted_at.is_(None))
            .order_by(Group.name)
        )
        rows = (await db.execute(stmt)).scalars().all()
        return list(rows)

    async def update_group(
        self, db: AsyncSession, group_id: UUID, user: User, payload: GroupUpdate
    ) -> Group:
        """Update a group's details. Only owner or admin can update."""
        group = await self.get_group_for_user(db, group_id, user)
        await self._require_role(db, group_id, user, {"owner", "admin"})

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(group, key, value)
        group.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(group)
        return group

    async def delete_group(self, db: AsyncSession, group_id: UUID, user: User) -> None:
        """Soft-delete a group. Only the owner can delete."""
        group = await self.get_group_for_user(db, group_id, user)
        if group.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the group owner can delete the group",
            )
        group.deleted_at = datetime.utcnow()
        await db.commit()

    async def remove_member(
        self, db: AsyncSession, group_id: UUID, user_id_to_remove: UUID, requesting_user: User
    ) -> None:
        """Remove a member from a group. Owner or admin can remove members."""
        group = await self.get_group_for_user(db, group_id, requesting_user)
        await self._require_role(db, group_id, requesting_user, {"owner", "admin"})

        if group.owner_id == user_id_to_remove:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the group owner",
            )

        removed = await self._member_repo(db).remove_member(group_id, user_id_to_remove)
        if not removed:
            raise HTTPException(status_code=404, detail="Member not found")

    async def change_member_role(
        self, db: AsyncSession, group_id: UUID, target_user_id: UUID, new_role: str, requesting_user: User
    ) -> dict[str, Any]:
        """Change a member's role. Only the owner can change roles."""
        group = await self.get_group_for_user(db, group_id, requesting_user)
        if group.owner_id != requesting_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the group owner can change roles",
            )

        if new_role not in ("admin", "member"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be 'admin' or 'member'",
            )

        # Use the repo to find the member
        members = await self._member_repo(db).list_by_group(group_id)
        member = None
        for m in members:
            if m.user_id == target_user_id:
                member = m
                break

        if member is None:
            raise HTTPException(status_code=404, detail="Member not found")

        member.role = new_role
        await db.commit()

        # Fetch the user to return display info
        user_stmt = select(User).where(User.id == target_user_id)
        u = (await db.execute(user_stmt)).scalar_one_or_none()

        return {
            "user_id": str(target_user_id),
            "username": u.username if u else None,
            "role": new_role,
        }

    async def _require_role(
        self, db: AsyncSession, group_id: UUID, user: User, allowed_roles: set[str]
    ) -> None:
        """Check that a user has one of the allowed roles in the group."""
        stmt = select(GroupMember).where(
            GroupMember.group_id == group_id, GroupMember.user_id == user.id
        )
        member = (await db.execute(stmt)).scalar_one_or_none()
        if member is None or member.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )


group_service = GroupService()
