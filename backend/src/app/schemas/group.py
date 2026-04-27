"""Pydantic schemas for group management endpoints."""

from datetime import datetime
from uuid import UUID
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, constr


class GroupCreate(BaseModel):
    """Payload for creating a new group."""

    model_config = ConfigDict(from_attributes=True)

    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    is_private: bool = True


class GroupUpdate(BaseModel):
    """Payload for updating an existing group (partial updates allowed)."""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None


class GroupSummary(BaseModel):
    """Compact representation used in list endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    is_private: bool
    owner_id: UUID
    avatar_url: Optional[str] = None
    created_at: datetime


class GroupDetail(GroupSummary):
    """Full representation for a single group, includes invite code and member count."""

    invite_code: str
    member_count: int
    description: Optional[str] = None
    updated_at: datetime


class AddMember(BaseModel):
    """Payload for adding a user to a group."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: Optional[constr(min_length=1, max_length=20)] = "member"


class RemoveMember(BaseModel):
    """Payload for removing a user from a group – currently empty, kept for symmetry."""

    model_config = ConfigDict(from_attributes=True)

    # No fields needed; the endpoint uses path parameters.
