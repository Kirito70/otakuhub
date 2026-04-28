"""Discussion reply model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime

if TYPE_CHECKING:
    from .discussion import Discussion
    from .user import User


class DiscussionReply(SQLModel, table=True):
    """Reply to a discussion thread."""

    id: UUID = Field(
        default_factory=UUID,
        primary_key=True,
        nullable=False
    )
    discussion_id: UUID = Field(foreign_key="discussion.id", nullable=False)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    parent_reply_id: Optional[UUID] = Field(default=None, foreign_key="discussionreply.id")  # for threading
    body: str = Field(nullable=False)
    has_spoilers: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Soft delete
    deleted_at: Optional[datetime] = Field(default=None)

    # Relationships
    discussion: Optional["Discussion"] = Relationship(back_populates="replies")
    user: Optional["User"] = Relationship(back_populates="discussion_replies")
    parent_reply: Optional["DiscussionReply"] = Relationship(
        back_populates="child_replies",

    )
    child_replies: list["DiscussionReply"] = Relationship(back_populates="parent_reply")

    # Create indexes for performance
    __table_args__ = (
        Index("idx_replies_discussion", "discussion_id", "created_at"),
    )
