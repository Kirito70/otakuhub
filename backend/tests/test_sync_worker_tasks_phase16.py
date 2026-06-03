"""Tests for worker tasks Phase 1.6 — import_user_list_task and process_new_episodes_task."""

from __future__ import annotations

from datetime import datetime, timedelta, UTC
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID

import pytest

from src.app.workers import sync_tasks


# ---------------------------------------------------------------------------
# import_user_list_task
# ---------------------------------------------------------------------------

class TestImportUserListTask:
    """Phase 1.6 — de-stubbed import_user_list_task."""

    def test_returns_expected_result_shape(self, monkeypatch):
        """Task returns a dict with the expected fields."""
        user_id = uuid4()
        provider = "anilist"
        username = "test_user"

        # Create a fake session
        fake_session = MagicMock()
        fake_session.add = MagicMock()
        fake_session.commit = AsyncMock()
        fake_session.execute = AsyncMock(
            return_value=SimpleNamespace(scalar_one_or_none=lambda: None)
        )

        # Fake async context manager
        fake_session_local = MagicMock()
        fake_session_local.__aenter__ = AsyncMock(return_value=fake_session)
        fake_session_local.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr("src.app.database.AsyncSessionLocal", lambda: fake_session_local)

        result = sync_tasks.import_user_list_task(user_id, provider, username)

        assert result["task"] == "sync.import_user_list"
        assert result["status"] == "completed"
        assert result["user_id"] == str(user_id)
        assert result["provider"] == provider
        assert result["processed_items"] == 0
        assert "job_id" in result
        assert "duration_ms" in result
        assert "timestamp" in result

    def test_raises_on_exception(self, monkeypatch):
        """Task raises on unexpected error inside the async _run."""
        def _broken_session():
            raise RuntimeError("DB unavailable")

        monkeypatch.setattr("src.app.database.AsyncSessionLocal", _broken_session)

        with pytest.raises(RuntimeError, match="DB unavailable"):
            sync_tasks.import_user_list_task(uuid4(), "anilist", "test_user")


# ---------------------------------------------------------------------------
# process_new_episodes_task
# ---------------------------------------------------------------------------

class TestProcessNewEpisodesTask:
    """Phase 1.6 — de-stubbed process_new_episodes_task."""

    def test_returns_empty_result_shape(self, monkeypatch):
        """Task returns expected fields when there are no new episodes/chapters."""
        # Use real models (imported inside the task) with a mocked session.
        # The real models are needed for select() to work properly; we just
        # control what the session returns.
        fake_result = MagicMock()
        fake_result.scalars.return_value.all.return_value = []

        fake_session = MagicMock()
        fake_session.add = MagicMock()
        fake_session.commit = AsyncMock()
        fake_session.execute = AsyncMock(return_value=fake_result)

        fake_session_local = MagicMock()
        fake_session_local.__aenter__ = AsyncMock(return_value=fake_session)
        fake_session_local.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr("src.app.database.AsyncSessionLocal", lambda: fake_session_local)

        result = sync_tasks.process_new_episodes_task()

        assert result["task"] == "sync.process_new_episodes"
        assert result["status"] == "completed"
        assert "new_episodes" in result
        assert "new_chapters" in result
        assert "notifications_created" in result
        assert "duration_ms" in result
        assert "timestamp" in result

    def test_detects_new_episodes_and_creates_notifications(self, monkeypatch):
        """Task creates notifications for users watching newly aired episodes."""
        media_id = uuid4()
        user_id = uuid4()
        now = datetime.now(UTC)

        # Build fake episode and entry objects that behave like real ORM objects
        fake_episode = SimpleNamespace(
            media_id=media_id,
            episode_number=15,
            title="Episode 15",
            air_date=now - timedelta(hours=2),
        )
        fake_entry = SimpleNamespace(
            user_id=user_id,
            media_id=media_id,
            status="watching",
        )

        # Configure multi-step execute returns
        ep_result = MagicMock()
        ep_result.scalars.return_value.all.return_value = [fake_episode]

        ch_result = MagicMock()
        ch_result.scalars.return_value.all.return_value = []

        watch_result = MagicMock()
        watch_result.scalars.return_value.all.return_value = [fake_entry]

        read_result = MagicMock()
        read_result.scalars.return_value.all.return_value = []

        fake_session = MagicMock()
        fake_session.add = MagicMock()
        fake_session.commit = AsyncMock()
        fake_session.execute = AsyncMock(
            side_effect=[ep_result, ch_result, watch_result, read_result]
        )

        fake_session_local = MagicMock()
        fake_session_local.__aenter__ = AsyncMock(return_value=fake_session)
        fake_session_local.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr("src.app.database.AsyncSessionLocal", lambda: fake_session_local)

        result = sync_tasks.process_new_episodes_task()

        assert result["new_episodes"] == 1
        assert result["new_chapters"] == 0
        assert result["notifications_created"] == 1
        assert result["status"] == "completed"

    def test_detects_new_chapters_and_creates_notifications(self, monkeypatch):
        """Task creates notifications for users reading newly published chapters."""
        media_id = uuid4()
        user_id = uuid4()
        now = datetime.now(UTC)

        fake_chapter = SimpleNamespace(
            media_id=media_id,
            chapter_number=42,
            title="Chapter 42",
            published_at=now - timedelta(hours=1),
        )
        fake_entry = SimpleNamespace(
            user_id=user_id,
            media_id=media_id,
            status="reading",
        )

        ep_result = MagicMock()
        ep_result.scalars.return_value.all.return_value = []

        ch_result = MagicMock()
        ch_result.scalars.return_value.all.return_value = [fake_chapter]

        # When episodes are empty, the watching-users query is skipped
        # So the 3rd execute call is for reading-users (not watching)
        read_result = MagicMock()
        read_result.scalars.return_value.all.return_value = [fake_entry]

        fake_session = MagicMock()
        fake_session.add = MagicMock()
        fake_session.commit = AsyncMock()
        fake_session.execute = AsyncMock(
            side_effect=[ep_result, ch_result, read_result]
        )

        fake_session_local = MagicMock()
        fake_session_local.__aenter__ = AsyncMock(return_value=fake_session)
        fake_session_local.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr("src.app.database.AsyncSessionLocal", lambda: fake_session_local)

        result = sync_tasks.process_new_episodes_task()

        assert result["new_episodes"] == 0
        assert result["new_chapters"] == 1
        assert result["notifications_created"] == 1
        assert result["status"] == "completed"

    def test_raises_on_exception(self, monkeypatch):
        """Task raises on unexpected error."""
        def _broken_session():
            raise RuntimeError("Processing failure")

        monkeypatch.setattr("src.app.database.AsyncSessionLocal", _broken_session)

        with pytest.raises(RuntimeError, match="Processing failure"):
            sync_tasks.process_new_episodes_task()
