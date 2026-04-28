"""Database enum definitions for OtakuHub."""

from enum import Enum


class MediaType(str, Enum):
    """Media type enumeration."""
    anime = "anime"
    manga = "manga"
    manhwa = "manhwa"
    manhua = "manhua"
    light_novel = "light_novel"
    novel = "novel"


class MediaFormat(str, Enum):
    """Media format enumeration."""
    TV = "TV"
    TV_SHORT = "TV_SHORT"
    MOVIE = "MOVIE"
    SPECIAL = "SPECIAL"
    OVA = "OVA"
    ONA = "ONA"
    MUSIC = "MUSIC"
    MANGA = "MANGA"
    MANHWA = "MANHWA"
    MANHUA = "MANHUA"
    ONE_SHOT = "ONE_SHOT"
    NOVEL = "NOVEL"
    LIGHT_NOVEL = "LIGHT_NOVEL"


class MediaStatus(str, Enum):
    """Media status enumeration."""
    releasing = "releasing"
    finished = "finished"
    not_yet_released = "not_yet_released"
    cancelled = "cancelled"
    hiatus = "hiatus"


class Season(str, Enum):
    """Season enumeration."""
    spring = "spring"
    summer = "summer"
    fall = "fall"
    winter = "winter"


class WatchStatus(str, Enum):
    """User watch/read status enumeration."""
    watching = "watching"
    reading = "reading"
    completed = "completed"
    paused = "paused"
    dropped = "dropped"
    plan_to_watch = "plan_to_watch"
    plan_to_read = "plan_to_read"
    rewatching = "rewatching"
    rereading = "rereading"


class RelationType(str, Enum):
    """Media relation type enumeration."""
    sequel = "sequel"
    prequel = "prequel"
    side_story = "side_story"
    parent = "parent"
    summary = "summary"
    alternative = "alternative"
    spin_off = "spin_off"
    adaptation = "adaptation"
    character = "character"
    other = "other"


class NotificationType(str, Enum):
    """Notification type enumeration."""
    new_episode = "new_episode"
    new_chapter = "new_chapter"
    friend_activity = "friend_activity"
    recommendation = "recommendation"
    watch_party_invite = "watch_party_invite"
    watch_party_reminder = "watch_party_reminder"
    system = "system"


class PartyStatus(str, Enum):
    """Watch party status enumeration."""
    scheduled = "scheduled"
    live = "live"
    completed = "completed"
    cancelled = "cancelled"


class RsvpStatus(str, Enum):
    """RSVP status enumeration."""
    pending = "pending"
    attending = "attending"
    declined = "declined"
