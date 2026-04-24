"""Watch party RSVP model for OtakuHub."""

from sqlmodel import SQLModel, Field, Relationship, Index
from typing import Optional, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
from src.app.models.enums import RsvpStatus

if TYPE_CHECKING:
    from .watch_party import WatchParty
    from .user import User


class WatchPartyRsvp(SQLModel, table=True):
    """RSVP for a watch party."""
    
    party_id: UUID = Field(
        foreign_key="watchparty.id", 
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="user.id", 
        primary_key=True,
        nullable=False
    )
    status: RsvpStatus = Field(default=RsvpStatus.pending)
    responded_at: Optional[datetime] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
        
    # Relationships
    party: Optional["WatchParty"] = Relationship(back_populates="rsvps")
    user: Optional["User"] = Relationship(back_populates="watch_party_rsvps")
    
    # Create indexes for performance
    __table_args__ = (
        Index("idx_rsvps_user", "user_id"),
    )