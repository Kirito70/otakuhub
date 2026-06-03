"""Initial database schema — all 28 tables.

Revision ID: 001
Revises: None
Create Date: 2026-06-04

This is the baseline migration capturing all current models.
UUID v7 is used for all primary keys (via Python generate_uuid7).
title_search uses TSVector type (portable via TSVector SQLAlchemy type).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enums (PostgreSQL only, skipped on SQLite) ---
    # These are defined as Python StrEnum in models/enums.py.
    # PostgreSQL CREATE TYPE statements would go here in a real PG migration.
    # On SQLite, VARCHAR columns store the string values directly.

    # --- media_entries ---
    op.create_table(
        "media_entries",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("title_romaji", sa.String(500), nullable=False),
        sa.Column("title_english", sa.String(500), nullable=True),
        sa.Column("title_native", sa.String(500), nullable=True),
        # Baseline: Text column. FTS migration upgrades to TSVECTOR on PostgreSQL.
        sa.Column("title_search", sa.Text(), nullable=True),
        sa.Column("media_type", sa.String(50), nullable=False),
        sa.Column("format", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="not_yet_released"),
        sa.Column("synopsis", sa.Text(), nullable=True),
        sa.Column("cover_image_large", sa.String(2048), nullable=True),
        sa.Column("cover_image_medium", sa.String(2048), nullable=True),
        sa.Column("banner_image", sa.String(2048), nullable=True),
        sa.Column("episode_count", sa.Integer(), nullable=True),
        sa.Column("chapter_count", sa.Integer(), nullable=True),
        sa.Column("volume_count", sa.Integer(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("average_score", sa.Float(), nullable=True),
        sa.Column("popularity", sa.Integer(), nullable=True),
        sa.Column("trending", sa.Integer(), nullable=True),
        sa.Column("season", sa.String(50), nullable=True),
        sa.Column("season_year", sa.SmallInteger(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("is_adult", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("country_of_origin", sa.String(2), nullable=True),
        sa.Column("metadata_synced_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- media_external_ids ---
    op.create_table(
        "media_external_ids",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("anilist_id", sa.Integer(), nullable=True, unique=True),
        sa.Column("mal_id", sa.Integer(), nullable=True),
        sa.Column("mangadex_id", sa.String(64), nullable=True),
        sa.Column("anidb_id", sa.Integer(), nullable=True),
        sa.Column("kitsu_id", sa.String(64), nullable=True),
        sa.Column("anime_planet_slug", sa.String(256), nullable=True),
        sa.Column("simkl_id", sa.Integer(), nullable=True),
        sa.Column("livechart_id", sa.Integer(), nullable=True),
        sa.Column("notify_moe_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- genres ---
    op.create_table(
        "genres",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
    )

    # --- studios ---
    op.create_table(
        "studios",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("anilist_id", sa.Integer(), nullable=True, unique=True),
    )

    # --- tags ---
    op.create_table(
        "tags",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("is_adult", sa.Boolean(), nullable=False, server_default="0"),
    )

    # --- Join tables ---
    op.create_table(
        "media_genre",
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("genre_id", sa.Uuid(), sa.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "media_studio",
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("studio_id", sa.Uuid(), sa.ForeignKey("studios.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("is_main", sa.Boolean(), nullable=False, server_default="0"),
    )

    op.create_table(
        "media_tag",
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Uuid(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("rank", sa.SmallInteger(), nullable=False, server_default="0"),
    )

    # --- related_media ---
    op.create_table(
        "related_media",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("source_media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("related_media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation_type", sa.String(50), nullable=False),
    )

    # --- episodes ---
    op.create_table(
        "episodes",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("episode_number", sa.SmallInteger(), nullable=False),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("air_date", sa.DateTime(), nullable=True),
        sa.Column("duration_minutes", sa.SmallInteger(), nullable=True),
        sa.Column("thumbnail_url", sa.String(2048), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- chapters ---
    op.create_table(
        "chapters",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chapter_number", sa.Float(), nullable=False),
        sa.Column("volume_number", sa.SmallInteger(), nullable=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("mangadex_chapter_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("avatar_url", sa.String(2048), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- refresh_tokens ---
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("device_name", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- external_auth ---
    op.create_table(
        "external_auth",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_user_id", sa.String(255), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=True),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(), nullable=True),
        sa.Column("provider_username", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- groups ---
    op.create_table(
        "groups",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("avatar_url", sa.String(2048), nullable=True),
        sa.Column("invite_code", sa.String(32), nullable=False, unique=True),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- group_members ---
    op.create_table(
        "group_members",
        sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- user_list_entry ---
    op.create_table(
        "user_list_entry",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("repeat_count", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "media_id", name="uq_user_list_entry_user_media"),
    )

    # --- list_entry_history ---
    op.create_table(
        "list_entry_history",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("entry_id", sa.Uuid(), sa.ForeignKey("user_list_entry.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("old_status", sa.String(50), nullable=True),
        sa.Column("new_status", sa.String(50), nullable=True),
        sa.Column("old_progress", sa.Integer(), nullable=True),
        sa.Column("new_progress", sa.Integer(), nullable=True),
        sa.Column("old_score", sa.Float(), nullable=True),
        sa.Column("new_score", sa.Float(), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- custom_lists ---
    op.create_table(
        "custom_lists",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("cover_image", sa.String(2048), nullable=True),
        sa.Column("sort_order", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- custom_list_entries ---
    op.create_table(
        "custom_list_entries",
        sa.Column("list_id", sa.Uuid(), sa.ForeignKey("custom_lists.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="RESTRICT"), primary_key=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("added_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- recommendations ---
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("from_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("to_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("is_acknowledged", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("from_user_id", "to_user_id", "media_id", name="uq_recommendation_users_media"),
    )

    # --- discussions ---
    op.create_table(
        "discussions",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("episode_number", sa.SmallInteger(), nullable=True),
        sa.Column("chapter_number", sa.Float(), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("has_spoilers", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- discussion_replies ---
    op.create_table(
        "discussion_replies",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("discussion_id", sa.Uuid(), sa.ForeignKey("discussions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("parent_reply_id", sa.Uuid(), sa.ForeignKey("discussion_replies.id", ondelete="SET_NULL"), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("has_spoilers", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- watch_parties ---
    op.create_table(
        "watch_parties",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("host_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("episode_number", sa.SmallInteger(), nullable=True),
        sa.Column("title", sa.String(300), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="scheduled"),
        sa.Column("stream_url", sa.String(2048), nullable=True),
        sa.Column("sync_url", sa.String(2048), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )

    # --- watch_party_rsvps ---
    op.create_table(
        "watch_party_rsvps",
        sa.Column("party_id", sa.Uuid(), sa.ForeignKey("watch_parties.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- notification_preferences ---
    op.create_table(
        "notification_preferences",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("new_episode", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("new_chapter", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("friend_activity", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("recommendations", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("watch_party_invite", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("watch_party_reminder", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("discord_webhook", sa.String(2048), nullable=True),
        sa.Column("telegram_chat_id", sa.String(100), nullable=True),
        sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("push_enabled", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("action_url", sa.String(2048), nullable=True),
        sa.Column("related_media_id", sa.Uuid(), sa.ForeignKey("media_entries.id", ondelete="SET_NULL"), nullable=True),
        sa.Column("related_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET_NULL"), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="0"),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # --- sync_jobs ---
    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="running"),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET_NULL"), nullable=True),
        sa.Column("total_items", sa.Integer(), nullable=True),
        sa.Column("processed_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_log", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )

    # --- Indexes ---
    op.create_index("idx_media_entries_title_search", "media_entries", ["title_search"])
    op.create_index("idx_media_entries_media_type", "media_entries", ["media_type"])
    op.create_index("idx_media_entries_status", "media_entries", ["status"])
    op.create_index("idx_media_entries_season", "media_entries", ["season_year", "season"])
    op.create_index("idx_media_entries_score", "media_entries", ["average_score"])
    op.create_index("idx_media_entries_synced_at", "media_entries", ["metadata_synced_at"])

    op.create_index("idx_media_ext_media_id", "media_external_ids", ["media_id"], unique=True)
    op.create_index("idx_media_ext_anilist", "media_external_ids", ["anilist_id"], unique=True, postgresql_where=sa.text("anilist_id IS NOT NULL"))
    op.create_index("idx_media_ext_mal", "media_external_ids", ["mal_id"], unique=True, postgresql_where=sa.text("mal_id IS NOT NULL"))
    op.create_index("idx_media_ext_mangadex", "media_external_ids", ["mangadex_id"], unique=True, postgresql_where=sa.text("mangadex_id IS NOT NULL"))

    op.create_index("idx_media_genres_genre", "media_genre", ["genre_id"])
    op.create_index("idx_media_studios_studio", "media_studio", ["studio_id"])
    op.create_index("idx_media_tags_tag", "media_tag", ["tag_id"])

    op.create_index("idx_related_media_source", "related_media", ["source_media_id"])
    op.create_index("idx_related_media_target", "related_media", ["related_media_id"])

    op.create_index("idx_episodes_media_id", "episodes", ["media_id"])
    op.create_index("idx_episodes_air_date", "episodes", ["air_date"])

    op.create_index("idx_chapters_media_id", "chapters", ["media_id"])
    op.create_index("idx_chapters_published_at", "chapters", ["published_at"])

    op.create_index("idx_users_username", "users", ["username"])
    op.create_index("idx_users_email", "users", ["email"])

    op.create_index("idx_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("idx_refresh_tokens_expires", "refresh_tokens", ["expires_at"])

    op.create_index("idx_external_auth_user_provider", "external_auth", ["user_id", "provider"], unique=True)

    op.create_index("idx_groups_invite_code", "groups", ["invite_code"])
    op.create_index("idx_group_members_user", "group_members", ["user_id"])

    op.create_index("idx_list_entries_user_id", "user_list_entry", ["user_id"])
    op.create_index("idx_list_entries_media_id", "user_list_entry", ["media_id"])
    op.create_index("idx_list_entries_status", "user_list_entry", ["user_id", "status"])
    op.create_index("idx_list_entries_updated", "user_list_entry", ["user_id", "updated_at"])
    op.create_index("idx_list_entries_user_media", "user_list_entry", ["user_id", "media_id"])

    op.create_index("idx_history_user_id", "list_entry_history", ["user_id", sa.text("created_at DESC")])
    op.create_index("idx_history_entry_id", "list_entry_history", ["entry_id"])
    op.create_index("idx_history_media_id", "list_entry_history", ["media_id"])
    op.create_index("idx_history_group_feed", "list_entry_history", ["user_id", sa.text("created_at DESC")])

    op.create_index("idx_custom_lists_user", "custom_lists", ["user_id"])
    op.create_index("idx_custom_list_entries_list", "custom_list_entries", ["list_id", "sort_order"])

    op.create_index("idx_recommendations_to_user", "recommendations", ["to_user_id", "is_acknowledged", sa.text("created_at DESC")])
    op.create_index("idx_recommendations_from", "recommendations", ["from_user_id"])

    op.create_index("idx_discussions_media_group", "discussions", ["media_id", "group_id", sa.text("created_at DESC")])
    op.create_index("idx_discussions_user", "discussions", ["user_id"])

    op.create_index("idx_replies_discussion", "discussion_replies", ["discussion_id", sa.text("created_at ASC")])

    op.create_index("idx_watch_parties_group", "watch_parties", ["group_id", sa.text("scheduled_at DESC")])
    op.create_index("idx_watch_parties_schedule", "watch_parties", ["scheduled_at"])

    op.create_index("idx_rsvps_user", "watch_party_rsvps", ["user_id"])

    op.create_index("idx_notifications_user", "notifications", ["user_id", "is_read", sa.text("created_at DESC")])
    op.create_index("idx_notifications_cleanup", "notifications", ["created_at"])

    op.create_index("idx_sync_jobs_type", "sync_jobs", ["job_type", sa.text("started_at DESC")])
    op.create_index("idx_sync_jobs_status", "sync_jobs", ["status"])


def downgrade() -> None:
    """Drop all tables in reverse order (respecting FK dependencies)."""
    op.drop_table("sync_jobs")
    op.drop_table("notifications")
    op.drop_table("notification_preferences")
    op.drop_table("watch_party_rsvps")
    op.drop_table("watch_parties")
    op.drop_table("discussion_replies")
    op.drop_table("discussions")
    op.drop_table("recommendations")
    op.drop_table("custom_list_entries")
    op.drop_table("custom_lists")
    op.drop_table("list_entry_history")
    op.drop_table("user_list_entry")
    op.drop_table("group_members")
    op.drop_table("groups")
    op.drop_table("external_auth")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    op.drop_table("chapters")
    op.drop_table("episodes")
    op.drop_table("related_media")
    op.drop_table("media_tag")
    op.drop_table("media_studio")
    op.drop_table("media_genre")
    op.drop_table("tags")
    op.drop_table("studios")
    op.drop_table("genres")
    op.drop_table("media_external_ids")
    op.drop_table("media_entries")
