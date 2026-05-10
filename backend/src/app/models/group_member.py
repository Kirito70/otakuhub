"""Group member model for OtakuHub."""

from sqlmodel import SQLModel, Field, Index
from uuid import UUID
from datetime import datetime


class GroupMember(SQLModel, table=True):
    """Group membership model."""

    group_id: UUID = Field(
        foreign_key="group.id",
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        primary_key=True,
        nullable=False
    )
    role: str = Field(default="member", max_length=20)  # 'owner', 'admin', 'member'
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    # Create indexes for performance
    __table_args__ = (
        Index("idx_group_members_user", "user_id"),
    )
