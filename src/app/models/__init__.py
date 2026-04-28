# ruff: noqa
"""Database models package."""

# Import all models here so they're registered with SQLModel
# This allows the migration system to discover them

from .enums import *  # noqa: F403,F401
# noqa: F401,F403,F821,E712,F841,E722
from .genre import Genre  # noqa: F401
from .studio import Studio  # noqa: F401
from .tag import Tag  # noqa: F401  # noqa: F401
from .media_entry import MediaEntry  # noqa: F401
from .media_external_ids import MediaExternalIds  # noqa: F401
from .media_genre import MediaGenre
from .media_studio import MediaStudio
from .media_tag import MediaTag
from .related_media import RelatedMedia
from .episode import Episode
from .chapter import Chapter
from .user import User
from .refresh_token import RefreshToken
from .external_auth import ExternalAuth
from .group import Group
from .group_member import GroupMember
from .user_list_entry import UserListEntry
from .list_entry_history import ListEntryHistory
from .custom_list import CustomList
from .custom_list_entry import CustomListEntry
from .recommendation import Recommendation
from .discussion import Discussion
from .discussion_reply import DiscussionReply
from .watch_party import WatchParty
from .watch_party_rsvp import WatchPartyRsvp
from .notification_preference import NotificationPreference
from .notification import Notification
from .sync_job import SyncJob
