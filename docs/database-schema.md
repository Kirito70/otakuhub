# OtakuHub — Complete Database Schema

## Phase Notes
- **2026-05-11 (Phase 15.1)**: No database schema changes required for frontend design tokens/theme semantics.
- **2026-05-11 (Phase 15.2)**: No database schema changes required for typography/spacing scale standardization.
- **2026-05-11 (Phase 15.3)**: No database schema changes required for shared UI primitive contracts.
- **2026-05-11 (Phase 15.4)**: No database schema changes required for dashboard template/layout contracts.
- **2026-05-11 (Phase 15.5)**: No database schema changes required for responsive behavior validation contracts.
- **2026-05-11 (Phase 16.1)**: No database schema changes required for login hardening behavior contract.
- **2026-05-11 (Phase 16.2)**: No database schema changes required for register hardening behavior contract.
- **2026-05-11 (Phase 16.3)**: No database schema changes required for setup bootstrap hardening behavior contract.
- **2026-05-11 (Phase 16.4)**: No database schema changes required for auth/setup test expansion contract.
- **2026-05-11 (Phase 17.1)**: No database schema changes required for Discover search tab behavior contract.
- **2026-05-11 (Phase 17.2)**: No database schema changes required for Discover trending tab behavior contract.
- **2026-05-11 (Phase 17.3)**: No database schema changes required for Discover new releases tab behavior contract.
- **2026-05-11 (Phase 17.4)**: No database schema changes required for Media Detail overview tab behavior contract.
- **2026-05-11 (Phase 17.5)**: No database schema changes required for Media Detail episodes/chapters tab behavior contract.
- **2026-05-11 (Phase 17.6)**: No database schema changes required for Media Detail relations tab behavior contract.
- **2026-05-11 (Phase 18.1)**: No database schema changes required for My List watching/reading tab behavior contract.
- **2026-05-11 (Phase 18.2)**: No database schema changes required for My List completed tab behavior contract.
- **2026-05-11 (Phase 18.3)**: No database schema changes required for My List paused tab behavior contract.
- **2026-05-11 (Phase 18.4)**: No database schema changes required for My List dropped tab behavior contract.
- **2026-05-11 (Phase 18.5)**: No database schema changes required for My List plan-to-watch/read tab behavior contract.
- **2026-05-11 (Phase 18.6)**: No database schema changes required for My List custom lists tab behavior contract.
- **2026-05-11 (Phase 18.7)**: No database schema changes required for Airing Calendar page behavior contract.
- **2026-05-11 (Phase 19.1)**: No database schema changes required for Feed group activity tab behavior contract.
- **2026-05-11 (Phase 19.2)**: No database schema changes required for Feed my activity tab behavior contract.
- **2026-05-11 (Phase 19.3)**: No database schema changes required for Recommendations inbox tab behavior contract.
- **2026-05-11 (Phase 19.4)**: No database schema changes required for Recommendations sent tab behavior contract.
- **2026-05-11 (Phase 19.5)**: No database schema changes required for Discussions threads tab behavior contract.
- **2026-05-11 (Phase 19.6)**: No database schema changes required for Discussions thread detail tab behavior contract.
- **2026-05-11 (Phase 19.7)**: No database schema changes required for Discussions create tab behavior contract.
- **2026-05-11 (Phase 19.8)**: No database schema changes required for social page test coverage contract.
- **2026-05-11 (Phase 20.1)**: No database schema changes required for Watch Party upcoming tab behavior contract.
- **2026-05-11 (Phase 20.2)**: No database schema changes required for Watch Party create tab behavior contract.
- **2026-05-11 (Phase 20.3)**: No database schema changes required for Watch Party detail tab behavior contract.
- **2026-05-11 (Phase 20.4)**: No database schema changes required for Watch Party past tab behavior contract.
- **2026-05-11 (Phase 20.5)**: No database schema changes required for Watch party test coverage contract.
- **2026-05-11 (Phase 21.1)**: No database schema changes required for Notifications inbox all tab behavior contract.
- **2026-05-11 (Phase 21.2)**: No database schema changes required for Notifications inbox unread tab behavior contract.
- **2026-05-11 (Phase 21.3)**: No database schema changes required for Notification preferences content tab behavior contract.
- **2026-05-11 (Phase 21.4)**: No database schema changes required for Notification preferences channels tab behavior contract.
- **2026-05-11 (Phase 22.1)**: No database schema changes required for Profile overview tab behavior contract.
- **2026-05-11 (Phase 22.2)**: No database schema changes required for Profile edit profile tab behavior contract.
- **2026-05-11 (Phase 22.3)**: No database schema changes required for Profile account & security tab behavior contract.
- **2026-05-11 (Phase 22.4)**: No database schema changes required for Profile tests contract.
- **2026-06-04 (Phase 2.1)**: All model PKs changed from `uuid4()` to `uuid7()` (RFC 9562). See ADR 077.
- **2026-06-04 (Phase 2.2)**: `media_entries.title_search` changed from `Text` to `TSVECTOR` (portable via `TSVector` SQLAlchemy type). GIN indexes, trigram indexes, and PostgreSQL trigger function added via Alembic migration. See ADR 077.
- **2026-06-04 (Phase 2.3)**: Alembic migration system initialized. Baseline migration `001_initial_tables.py` captures all current tables. See ADR 077.
- **2026-06-04 (Phase 2.4)**: Default `DATABASE_URL` changed to `postgresql+asyncpg://postgres:postgres@localhost:5432/otakuhub`. Pool settings wired to engine. SQLite retained for tests only. See ADR 077.
- **2026-06-04 (Phase 2.5)**: Explicit `UniqueConstraint` declarations added to `user_list_entry` and `recommendation` models. See ADR 077.
- **2026-06-05 (Urgent source-provider design)**: Add source-provider registry design for Anikoto/MegaPlay and future playback providers. `media_external_ids` remains canonical metadata cross-reference; provider-specific series and episode IDs are stored in `media_source_mappings` and `media_source_episodes`. See ADR 078.
- **2026-06-06 (ADR 078 implementation)**: Implemented `media_source_mappings` and `media_source_episodes` via Alembic revision `002`; no raw media segment URLs are stored and AniList remains canonical cross-reference key.
- **2026-06-06 (Payload + streaming storage)**: Added `source_payload` (JSONB) and `source_titles` (JSONB) to `media_source_mappings` for full API response archival and structured multilingual titles. Renamed `embed_path` → `embed_url` (VARCHAR(2048)) on `media_source_episodes`, added `embed_urls` (JSONB) for all language→URL mappings, `source_payload` (JSONB) for raw episode payload, and `details_synced_at` per Alembic revision `003`. See full provider payload plan.

## PostgreSQL Extensions Required

> **Note**: `pg_uuidv7` is optional — the app uses a Python implementation of UUID v7 (RFC 9562) for portability across SQLite and PostgreSQL. The extension can be used for server-side generation if desired but is not required.

```sql
CREATE EXTENSION IF NOT EXISTS "pg_trgm";         -- Trigram similarity for search (FTS migration)
CREATE EXTENSION IF NOT EXISTS "unaccent";         -- Accent-insensitive search (FTS migration)
CREATE EXTENSION IF NOT EXISTS "btree_gin";        -- GIN on btree-able types (FTS migration)
-- Optional: CREATE EXTENSION IF NOT EXISTS "pg_uuidv7";  -- Not required — Python uuid7 used instead
```

---

## Enumerations

```sql
CREATE TYPE media_type_enum    AS ENUM ('anime', 'manga', 'manhwa', 'manhua', 'light_novel', 'novel');
CREATE TYPE media_format_enum  AS ENUM ('TV', 'TV_SHORT', 'MOVIE', 'SPECIAL', 'OVA', 'ONA', 'MUSIC', 'MANGA', 'MANHWA', 'MANHUA', 'ONE_SHOT', 'NOVEL', 'LIGHT_NOVEL');
CREATE TYPE media_status_enum  AS ENUM ('releasing', 'finished', 'not_yet_released', 'cancelled', 'hiatus');
CREATE TYPE season_enum        AS ENUM ('spring', 'summer', 'fall', 'winter');
CREATE TYPE watch_status_enum  AS ENUM ('watching', 'reading', 'completed', 'paused', 'dropped', 'plan_to_watch', 'plan_to_read', 'rewatching', 'rereading');
CREATE TYPE relation_type_enum AS ENUM ('sequel', 'prequel', 'side_story', 'parent', 'summary', 'alternative', 'spin_off', 'adaptation', 'character', 'other');
CREATE TYPE notif_type_enum    AS ENUM ('new_episode', 'new_chapter', 'friend_activity', 'recommendation', 'watch_party_invite', 'watch_party_reminder', 'system');
CREATE TYPE party_status_enum  AS ENUM ('scheduled', 'live', 'completed', 'cancelled');
CREATE TYPE rsvp_status_enum   AS ENUM ('pending', 'attending', 'declined');
```

---

## Core Media Catalogue

### `media_entries`
The canonical table for every anime, manga, and manhwa known to the system.
Seeded from `anime-offline-database`, enriched by AniList and MangaDex.

```sql
CREATE TABLE media_entries (
    id                  UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    title_romaji        VARCHAR(500) NOT NULL,
    title_english       VARCHAR(500),
    title_native        VARCHAR(500),
    title_search        TSVECTOR,           -- GIN indexed, auto-updated via trigger
    media_type          media_type_enum    NOT NULL,
    format              media_format_enum,
    status              media_status_enum  NOT NULL DEFAULT 'not_yet_released',
    synopsis            TEXT,
    cover_image_large   VARCHAR(2048),
    cover_image_medium  VARCHAR(2048),
    banner_image        VARCHAR(2048),
    episode_count       INT,
    chapter_count       INT,
    volume_count        INT,
    duration_minutes    INT,                -- per-episode duration for anime
    average_score       FLOAT,             -- 0.0–10.0, from AniList
    popularity          INT,               -- AniList popularity rank
    trending            INT,               -- AniList trending score
    season              season_enum,
    season_year         SMALLINT,
    start_date          DATE,
    end_date            DATE,
    is_adult            BOOLEAN    NOT NULL DEFAULT FALSE,
    country_of_origin   CHAR(2),           -- ISO 3166-1 alpha-2 (JP, KR, CN)
    metadata_synced_at  TIMESTAMPTZ,       -- NULL = needs backfill
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at          TIMESTAMPTZ
);

-- Full-text search index (covers all three title variants)
CREATE INDEX idx_media_entries_title_search  ON media_entries USING GIN (title_search);
-- Filtering indexes
CREATE INDEX idx_media_entries_media_type    ON media_entries (media_type);
CREATE INDEX idx_media_entries_status        ON media_entries (status);
CREATE INDEX idx_media_entries_season        ON media_entries (season_year, season);
CREATE INDEX idx_media_entries_score         ON media_entries (average_score DESC NULLS LAST);
CREATE INDEX idx_media_entries_synced_at     ON media_entries (metadata_synced_at NULLS FIRST); -- find unsynced
-- Trigram index for partial-match search
CREATE INDEX idx_media_entries_romaji_trgm   ON media_entries USING GIN (title_romaji gin_trgm_ops);
CREATE INDEX idx_media_entries_english_trgm  ON media_entries USING GIN (title_english gin_trgm_ops);

-- Auto-update tsvector on insert/update
CREATE OR REPLACE FUNCTION update_media_title_search() RETURNS TRIGGER AS $$
BEGIN
    NEW.title_search :=
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.title_english, ''))), 'A') ||
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.title_romaji, ''))), 'B') ||
        setweight(to_tsvector('simple', unaccent(coalesce(NEW.title_native, ''))), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER trg_media_title_search
    BEFORE INSERT OR UPDATE ON media_entries
    FOR EACH ROW EXECUTE FUNCTION update_media_title_search();
```

### `media_external_ids`
Cross-reference table mapping our internal UUID to IDs on every external platform.
One row per media entry. All external IDs are nullable — not every title exists everywhere.

```sql
CREATE TABLE media_external_ids (
    id              UUID    PRIMARY KEY DEFAULT uuid_generate_v7(),
    media_id        UUID    NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    anilist_id      INT     UNIQUE,     -- canonical cross-ref key
    mal_id          INT,
    mangadex_id     VARCHAR(64),        -- UUID string from MangaDex
    anidb_id        INT,
    kitsu_id        VARCHAR(64),
    anime_planet_slug VARCHAR(256),
    simkl_id        INT,
    livechart_id    INT,
    notify_moe_id   VARCHAR(64),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_media_ext_media_id   ON media_external_ids (media_id);
CREATE UNIQUE INDEX idx_media_ext_anilist     ON media_external_ids (anilist_id) WHERE anilist_id IS NOT NULL;
CREATE UNIQUE INDEX idx_media_ext_mal         ON media_external_ids (mal_id) WHERE mal_id IS NOT NULL;
CREATE UNIQUE INDEX idx_media_ext_mangadex    ON media_external_ids (mangadex_id) WHERE mangadex_id IS NOT NULL;
```

### `media_source_mappings` (ADR 078)
Provider/source registry for external catalog/playback systems. This is separate from `media_external_ids` because playback providers need source names, provider-specific IDs, availability, matching confidence, and source freshness. `media_id` is nullable to allow safe storage of unmatched provider titles until manual/canonical matching is possible.

```sql
CREATE TABLE media_source_mappings (
    id                    UUID         PRIMARY KEY DEFAULT uuid_generate_v7(),
    media_id              UUID         REFERENCES media_entries(id) ON DELETE SET NULL,
    source                VARCHAR(50)  NOT NULL,     -- 'anikoto', 'megaplay', future provider names
    source_media_id       VARCHAR(128) NOT NULL,     -- provider series/catalog ID
    source_slug           VARCHAR(300),              -- provider slug/path when available
    source_url            VARCHAR(2048),             -- provider detail/catalog URL when safe to store
    source_title          VARCHAR(500),              -- title exactly as returned by provider
    source_title_normalized VARCHAR(500),            -- lower/unaccent/punctuation-stripped matching key
    source_payload_hash   VARCHAR(64),               -- SHA-256 hash for change detection
    source_payload        JSONB,                     -- full raw API response for this series/mapping
    source_titles         JSONB,                     -- structured multilingual titles extracted from provider
    mapping_status        VARCHAR(20)  NOT NULL DEFAULT 'matched', -- matched|unmatched|ignored|stale
    match_confidence      NUMERIC(5,2) NOT NULL DEFAULT 100.00,
    is_streaming_enabled  BOOLEAN      NOT NULL DEFAULT FALSE,
    has_sub               BOOLEAN      NOT NULL DEFAULT FALSE,
    has_dub               BOOLEAN      NOT NULL DEFAULT FALSE,
    episode_count         INT,
    first_seen_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_seen_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    details_synced_at     TIMESTAMPTZ,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at            TIMESTAMPTZ,
    UNIQUE (source, source_media_id)
);

CREATE INDEX idx_media_source_mappings_media ON media_source_mappings (media_id, source) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_source_mappings_source_seen ON media_source_mappings (source, last_seen_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_source_mappings_status ON media_source_mappings (source, mapping_status) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_source_mappings_title_trgm ON media_source_mappings USING GIN (source_title_normalized gin_trgm_ops);
```

Rationale:
- `source` + `source_media_id` is the provider conflict key.
- `media_id` is nullable so uncertain Anikoto rows do not create duplicate canonical media entries.
- `mapping_status` and `match_confidence` support manual reconciliation.
- `source_payload` stores the complete raw provider API response for archival and inspection — any provider-specific fields that lack dedicated columns are preserved here.
- `source_titles` stores structured multilingual title variants (romaji, native, alternative, english, all) extracted from the provider's often-comma-separated title fields.
- `details_synced_at` and `last_seen_at` support daily recent refresh and stale detection.

### `media_source_episodes` (ADR 078)
Episode-level provider IDs and language availability. This table lets future playback resolve from our media/episode context to provider-specific episode IDs without storing direct raw stream URLs.

```sql
CREATE TABLE media_source_episodes (
    id                    UUID         PRIMARY KEY DEFAULT uuid_generate_v7(),
    mapping_id            UUID         NOT NULL REFERENCES media_source_mappings(id) ON DELETE CASCADE,
    media_id              UUID         REFERENCES media_entries(id) ON DELETE SET NULL,
    episode_id            UUID         REFERENCES episodes(id) ON DELETE SET NULL,
    source                VARCHAR(50)  NOT NULL,      -- denormalized for fast lookup; matches mapping.source
    source_episode_id     VARCHAR(128) NOT NULL,      -- Anikoto/MegaPlay/legacy HiAnime episode_embed_id
    episode_number        NUMERIC(8,2) NOT NULL,
    title                 VARCHAR(500),
    language              VARCHAR(20)  NOT NULL DEFAULT 'sub', -- sub|dub|raw|unknown
    embed_url             VARCHAR(2048),               -- full safe MegaPlay embed URL for this language
    embed_urls            JSONB,                       -- all language→URL mappings from provider (e.g. {"sub": "https://...", "dub": "https://..."})
    source_payload        JSONB,                       -- full raw API episode response
    details_synced_at     TIMESTAMPTZ,                 -- when episode detail was last fetched
    is_available          BOOLEAN      NOT NULL DEFAULT TRUE,
    first_seen_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    last_seen_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    deleted_at            TIMESTAMPTZ,
    UNIQUE (source, source_episode_id, language)
);

CREATE INDEX idx_media_source_episodes_mapping ON media_source_episodes (mapping_id, episode_number);
CREATE INDEX idx_media_source_episodes_media ON media_source_episodes (media_id, episode_number, language) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_source_episodes_available ON media_source_episodes (source, is_available, last_seen_at DESC) WHERE deleted_at IS NULL;
```

Rationale:
- Supports Anikoto `episode_embed_id` and future providers with episode-level IDs.
- `language` allows sub/dub rows to differ without overloading one ID field.
- `embed_url` stores the full safe MegaPlay embed URL for the current row's language; `embed_urls` stores the complete language→URL mapping from the source API.
- `details_synced_at` and `last_seen_at` support daily recent refresh and stale detection.

### `genres`
```sql
CREATE TABLE genres (
    id      UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    name    VARCHAR(100) NOT NULL UNIQUE,
    slug    VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE media_genres (
    media_id  UUID NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    genre_id  UUID NOT NULL REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (media_id, genre_id)
);
CREATE INDEX idx_media_genres_genre ON media_genres (genre_id);
```

### `studios`
```sql
CREATE TABLE studios (
    id         UUID         PRIMARY KEY DEFAULT uuid_generate_v7(),
    name       VARCHAR(255) NOT NULL UNIQUE,
    anilist_id INT          UNIQUE
);
CREATE TABLE media_studios (
    media_id   UUID    NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    studio_id  UUID    NOT NULL REFERENCES studios(id) ON DELETE CASCADE,
    is_main    BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (media_id, studio_id)
);
```

### `tags`
```sql
CREATE TABLE tags (
    id          UUID         PRIMARY KEY DEFAULT uuid_generate_v7(),
    name        VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category    VARCHAR(100),
    is_adult    BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE media_tags (
    media_id  UUID    NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    tag_id    UUID    NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    rank      SMALLINT NOT NULL DEFAULT 0,     -- AniList tag relevance 0–100
    PRIMARY KEY (media_id, tag_id)
);
CREATE INDEX idx_media_tags_tag ON media_tags (tag_id);
```

### `related_media`
```sql
CREATE TABLE related_media (
    id               UUID               PRIMARY KEY DEFAULT uuid_generate_v7(),
    source_media_id  UUID               NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    related_media_id UUID               NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    relation_type    relation_type_enum NOT NULL,
    UNIQUE (source_media_id, related_media_id, relation_type)
);
CREATE INDEX idx_related_media_source ON related_media (source_media_id);
```

### `episodes`
Airing schedule data for anime. Chapter release data for manga in `chapters`.

```sql
CREATE TABLE episodes (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    media_id        UUID        NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    episode_number  SMALLINT    NOT NULL,
    title           VARCHAR(500),
    air_date        TIMESTAMPTZ,
    duration_minutes SMALLINT,
    thumbnail_url   VARCHAR(2048),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (media_id, episode_number)
);
CREATE INDEX idx_episodes_media_id  ON episodes (media_id);
CREATE INDEX idx_episodes_air_date  ON episodes (air_date);
```

### `chapters`
```sql
CREATE TABLE chapters (
    id                  UUID    PRIMARY KEY DEFAULT uuid_generate_v7(),
    media_id            UUID    NOT NULL REFERENCES media_entries(id) ON DELETE CASCADE,
    chapter_number      FLOAT   NOT NULL,       -- float allows 12.5 for sub-chapters
    volume_number       SMALLINT,
    title               VARCHAR(500),
    published_at        TIMESTAMPTZ,
    mangadex_chapter_id VARCHAR(64),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (media_id, chapter_number)
);
CREATE INDEX idx_chapters_media_id     ON chapters (media_id);
CREATE INDEX idx_chapters_published_at ON chapters (published_at DESC);
```

---

## Users & Auth

### `users`
```sql
CREATE TABLE users (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    username        VARCHAR(50) NOT NULL UNIQUE,
    display_name    VARCHAR(100),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    avatar_url      VARCHAR(2048),
    bio             TEXT,
    timezone        VARCHAR(64) NOT NULL DEFAULT 'UTC',
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    is_admin        BOOLEAN     NOT NULL DEFAULT FALSE,
    last_seen_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE UNIQUE INDEX idx_users_username ON users (LOWER(username));  -- case-insensitive
CREATE UNIQUE INDEX idx_users_email    ON users (LOWER(email));
```

### `refresh_tokens`
```sql
CREATE TABLE refresh_tokens (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(255) NOT NULL UNIQUE,    -- SHA-256 of the actual token
    device_name VARCHAR(255),
    ip_address  VARCHAR(45),
    expires_at  TIMESTAMPTZ NOT NULL,
    revoked_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens (user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens (expires_at);
```

### `external_auth` (for future AniList/MAL OAuth)
```sql
CREATE TABLE external_auth (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider        VARCHAR(50) NOT NULL,    -- 'anilist', 'myanimelist'
    provider_user_id VARCHAR(255) NOT NULL,
    access_token    TEXT,                    -- encrypted at rest
    refresh_token   TEXT,                    -- encrypted at rest
    token_expires_at TIMESTAMPTZ,
    provider_username VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, provider)
);
```

---

## Friend Groups

### `groups`
```sql
CREATE TABLE groups (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    avatar_url  VARCHAR(2048),
    invite_code VARCHAR(32)  NOT NULL UNIQUE DEFAULT encode(gen_random_bytes(12), 'hex'),
    owner_id    UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    is_private  BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ
);
```

### `group_members`
```sql
CREATE TABLE group_members (
    group_id    UUID        NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        VARCHAR(20) NOT NULL DEFAULT 'member',   -- 'owner', 'admin', 'member'
    joined_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (group_id, user_id)
);
CREATE INDEX idx_group_members_user ON group_members (user_id);
```

---

## Tracking & Lists

### `user_list_entries`
The core tracking table. One row per user per media title.

```sql
CREATE TABLE user_list_entries (
    id              UUID              PRIMARY KEY DEFAULT uuid_generate_v7(),
    user_id         UUID              NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    media_id        UUID              NOT NULL REFERENCES media_entries(id) ON DELETE RESTRICT,
    status          watch_status_enum NOT NULL,
    progress        INT               NOT NULL DEFAULT 0,   -- episodes watched / chapters read
    score           FLOAT,                                  -- user's personal score 0.0–10.0
    notes           TEXT,
    is_private      BOOLEAN           NOT NULL DEFAULT FALSE,
    repeat_count    SMALLINT          NOT NULL DEFAULT 0,   -- rewatch/reread count
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ       NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE (user_id, media_id)
);
CREATE INDEX idx_list_entries_user_id  ON user_list_entries (user_id);
CREATE INDEX idx_list_entries_media_id ON user_list_entries (media_id);
CREATE INDEX idx_list_entries_status   ON user_list_entries (user_id, status);
CREATE INDEX idx_list_entries_updated  ON user_list_entries (user_id, updated_at DESC);
```

### `list_entry_history`
Append-only log of every status/progress change. Powers the activity feed.

```sql
CREATE TABLE list_entry_history (
    id              UUID              PRIMARY KEY DEFAULT uuid_generate_v7(),
    entry_id        UUID              NOT NULL REFERENCES user_list_entries(id) ON DELETE CASCADE,
    user_id         UUID              NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    media_id        UUID              NOT NULL REFERENCES media_entries(id) ON DELETE RESTRICT,
    event_type      VARCHAR(50)       NOT NULL,   -- 'status_changed', 'progress_updated', 'score_set', 'added', 'removed'
    old_status      watch_status_enum,
    new_status      watch_status_enum,
    old_progress    INT,
    new_progress    INT,
    old_score       FLOAT,
    new_score       FLOAT,
    note            TEXT,                          -- optional note attached to this update
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_history_user_id   ON list_entry_history (user_id, created_at DESC);
CREATE INDEX idx_history_entry_id  ON list_entry_history (entry_id);
CREATE INDEX idx_history_media_id  ON list_entry_history (media_id);
-- Powers group activity feed
CREATE INDEX idx_history_group_feed ON list_entry_history (user_id, created_at DESC) INCLUDE (media_id, event_type, new_status, new_progress);
```

### `custom_lists`
User-created curated lists ("Best Isekai", "Watch with friends").

```sql
CREATE TABLE custom_lists (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    is_public   BOOLEAN     NOT NULL DEFAULT FALSE,   -- visible to group members
    cover_image VARCHAR(2048),
    sort_order  SMALLINT    NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ
);
CREATE INDEX idx_custom_lists_user ON custom_lists (user_id);
```

### `custom_list_entries`
```sql
CREATE TABLE custom_list_entries (
    list_id     UUID    NOT NULL REFERENCES custom_lists(id) ON DELETE CASCADE,
    media_id    UUID    NOT NULL REFERENCES media_entries(id) ON DELETE RESTRICT,
    sort_order  INT     NOT NULL DEFAULT 0,
    note        TEXT,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (list_id, media_id)
);
CREATE INDEX idx_custom_list_entries_list ON custom_list_entries (list_id, sort_order);
```

---

## Social Features

### `recommendations`
A friend formally recommending a title to specific people.

```sql
CREATE TABLE recommendations (
    id              UUID    PRIMARY KEY DEFAULT uuid_generate_v7(),
    from_user_id    UUID    NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    to_user_id      UUID    NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    media_id        UUID    NOT NULL REFERENCES media_entries(id) ON DELETE RESTRICT,
    message         TEXT,
    is_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
    acknowledged_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    UNIQUE (from_user_id, to_user_id, media_id)   -- can't recommend the same thing twice
);
CREATE INDEX idx_recommendations_to_user ON recommendations (to_user_id, is_acknowledged, created_at DESC);
CREATE INDEX idx_recommendations_from    ON recommendations (from_user_id);
```

### `discussions`
Per-title discussion threads, scoped to a group.

```sql
CREATE TABLE discussions (
    id          UUID    PRIMARY KEY DEFAULT uuid_generate_v7(),
    media_id    UUID    NOT NULL REFERENCES media_entries(id) ON DELETE RESTRICT,
    group_id    UUID    NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    user_id     UUID    NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title       VARCHAR(300),
    episode_number SMALLINT,    -- NULL = general; set = episode-specific discussion
    chapter_number FLOAT,
    body        TEXT    NOT NULL,
    has_spoilers BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at  TIMESTAMPTZ
);
CREATE INDEX idx_discussions_media_group ON discussions (media_id, group_id, created_at DESC);
CREATE INDEX idx_discussions_user        ON discussions (user_id);
```

### `discussion_replies`
```sql
CREATE TABLE discussion_replies (
    id              UUID    PRIMARY KEY DEFAULT uuid_generate_v7(),
    discussion_id   UUID    NOT NULL REFERENCES discussions(id) ON DELETE CASCADE,
    user_id         UUID    NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    parent_reply_id UUID    REFERENCES discussion_replies(id) ON DELETE SET NULL,  -- for threading
    body            TEXT    NOT NULL,
    has_spoilers    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_replies_discussion ON discussion_replies (discussion_id, created_at ASC);
```

---

## Watch Party

### `watch_parties`
```sql
CREATE TABLE watch_parties (
    id              UUID              PRIMARY KEY DEFAULT uuid_generate_v7(),
    group_id        UUID              NOT NULL REFERENCES groups(id) ON DELETE CASCADE,
    host_user_id    UUID              NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    media_id        UUID              NOT NULL REFERENCES media_entries(id) ON DELETE RESTRICT,
    episode_number  SMALLINT,
    title           VARCHAR(300),
    scheduled_at    TIMESTAMPTZ       NOT NULL,
    status          party_status_enum NOT NULL DEFAULT 'scheduled',
    stream_url      VARCHAR(2048),               -- HiAnime, Crunchyroll, etc. deep link
    sync_url        VARCHAR(2048),               -- SyncParty / Rave link if using sync tool
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);
CREATE INDEX idx_watch_parties_group    ON watch_parties (group_id, scheduled_at DESC);
CREATE INDEX idx_watch_parties_schedule ON watch_parties (scheduled_at) WHERE status = 'scheduled';
```

### `watch_party_rsvps`
```sql
CREATE TABLE watch_party_rsvps (
    party_id    UUID              NOT NULL REFERENCES watch_parties(id) ON DELETE CASCADE,
    user_id     UUID              NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status      rsvp_status_enum  NOT NULL DEFAULT 'pending',
    responded_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (party_id, user_id)
);
CREATE INDEX idx_rsvps_user ON watch_party_rsvps (user_id);
```

---

## Notifications

### `notification_preferences`
```sql
CREATE TABLE notification_preferences (
    user_id             UUID    PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    new_episode         BOOLEAN NOT NULL DEFAULT TRUE,
    new_chapter         BOOLEAN NOT NULL DEFAULT TRUE,
    friend_activity     BOOLEAN NOT NULL DEFAULT TRUE,
    recommendations     BOOLEAN NOT NULL DEFAULT TRUE,
    watch_party_invite  BOOLEAN NOT NULL DEFAULT TRUE,
    watch_party_reminder BOOLEAN NOT NULL DEFAULT TRUE,
    -- Delivery channels (via Apprise)
    discord_webhook     VARCHAR(2048),
    telegram_chat_id    VARCHAR(100),
    email_enabled       BOOLEAN NOT NULL DEFAULT FALSE,
    push_enabled        BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### `notifications`
```sql
CREATE TABLE notifications (
    id              UUID            PRIMARY KEY DEFAULT uuid_generate_v7(),
    user_id         UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type            notif_type_enum NOT NULL,
    title           VARCHAR(300)    NOT NULL,
    body            TEXT,
    action_url      VARCHAR(2048),
    related_media_id UUID           REFERENCES media_entries(id) ON DELETE SET NULL,
    related_user_id  UUID           REFERENCES users(id) ON DELETE SET NULL,
    is_read         BOOLEAN         NOT NULL DEFAULT FALSE,
    read_at         TIMESTAMPTZ,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notifications_user     ON notifications (user_id, is_read, created_at DESC);
CREATE INDEX idx_notifications_cleanup  ON notifications (created_at) WHERE is_read = TRUE; -- for TTL cleanup job
```

---

## Sync Metadata

### `sync_jobs`
Tracks every run of the background sync pipeline.

```sql
CREATE TABLE sync_jobs (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v7(),
    job_type        VARCHAR(50) NOT NULL,   -- 'seed', 'backfill_anilist', 'weekly_refresh', 'user_import'
    status          VARCHAR(20) NOT NULL DEFAULT 'running',  -- 'running', 'completed', 'failed', 'partial'
    user_id         UUID        REFERENCES users(id) ON DELETE SET NULL,  -- NULL for system jobs
    total_items     INT,
    processed_items INT         NOT NULL DEFAULT 0,
    failed_items    INT         NOT NULL DEFAULT 0,
    error_log       TEXT,
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_sync_jobs_type   ON sync_jobs (job_type, started_at DESC);
CREATE INDEX idx_sync_jobs_status ON sync_jobs (status) WHERE status = 'running';
```

---

## Table Summary

| Table | Purpose | Rows (estimate) |
|-------|---------|----------------|
| `media_entries` | All anime/manga/manhwa | ~30,000 seeded, grows weekly |
| `media_external_ids` | Cross-reference IDs | 1:1 with media_entries |
| `media_source_mappings` | Provider/source series IDs and availability mappings | 0–N per media title |
| `media_source_episodes` | Provider/source episode IDs with streaming URLs and payloads by language | 0–N per mapped source title |
| `genres` | Genre lookup | ~50 |
| `studios` | Studio lookup | ~1,000 |
| `tags` | Tag lookup | ~600 |
| `media_genres` | M:M join | ~150,000 |
| `media_studios` | M:M join | ~30,000 |
| `media_tags` | M:M join | ~500,000 |
| `related_media` | Sequel/prequel links | ~80,000 |
| `episodes` | Airing schedule | ~500,000 |
| `chapters` | Chapter releases | ~1,000,000 |
| `users` | Group members | ~20 (private app) |
| `refresh_tokens` | Auth tokens | ~100 |
| `external_auth` | AniList/MAL OAuth | ~20 |
| `groups` | Friend groups | ~5 |
| `group_members` | Group membership | ~100 |
| `user_list_entries` | Tracking data | ~5,000 |
| `list_entry_history` | Activity log | ~50,000 |
| `custom_lists` | Curated lists | ~100 |
| `custom_list_entries` | List items | ~1,000 |
| `recommendations` | Friend recs | ~500 |
| `discussions` | Title discussions | ~500 |
| `discussion_replies` | Discussion replies | ~5,000 |
| `watch_parties` | Watch party events | ~200 |
| `watch_party_rsvps` | RSVPs | ~1,000 |
| `notification_preferences` | Notif settings | 1:1 with users |
| `notifications` | Notification inbox | ~10,000 |
| `sync_jobs` | Pipeline audit log | ~1,000 |
