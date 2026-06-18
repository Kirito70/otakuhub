"""Watch party RSVP model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from sqlalchemy import String
from src.app.models.enums import RsvpStatus

if TYPE_CHECKING:
    from .watch_party import WatchParty
    from .user import User


class WatchPartyRsvp(SQLModel, table=True):
    """RSVP for a watch party."""

    __tablename__ = "watch_party_rsvps"

    party_id: UUID = Field(
        foreign_key="watch_parties.id",
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="users.id",
        primary_key=True,
        nullable=False
    )
    status: RsvpStatus = Field(default=RsvpStatus.pending, sa_type=String)
    responded_at: Optional[datetime] = Field(default=None)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    party: Optional["WatchParty"] = Relationship()
    user: Optional["User"] = Relationship()

    # Create indexes for performance
    __table_args__ = (
        Index("idx_rsvps_user", "user_id"),
    )
