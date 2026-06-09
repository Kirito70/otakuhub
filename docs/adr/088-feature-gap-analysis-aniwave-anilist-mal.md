# ADR 088 — Feature Gap Analysis: AniWave × AniList × MyAnimeList

**Status**: Proposed
**Date**: 2026-06-08

## Context

OtakuHub's initial feature set (Phases 1–24) focused on metadata sync, user tracking, and social features. ADRs 079–087 (Phases 25–32) define the streaming-first redesign with playback. However, a comprehensive comparison against the three major anime platforms reveals significant feature gaps.

This ADR catalogues **every feature** from AniWave (streaming), AniList (tracking/discovery), and MyAnimeList (community) and maps them against OtakuHub's current + planned state.

## Feature Comparison Matrix

### Legend
- ✅ **Done** — Implemented and tested
- 🚧 **Planned** — In ADRs 079–087 (Phases 25–32)
- 🔲 **Gap** — Not in any plan
- ❌ **Out of scope** — Deliberately excluded

---

### 1. MEDIA DATABASE & METADATA

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Anime & manga entries with full metadata | ✅ | ✅ | ✅ | ✅ | 3 |
| Genres, studios, tags | ✅ | ✅ | ✅ | ✅ | 3 |
| Related media (sequel, prequel, etc.) | ✅ | ✅ | ✅ | ✅ | 3 |
| External IDs (AniList, MAL, MangaDex, etc.) | ❌ | ✅ | ✅ | ✅ | 3 |
| Full-text search across titles | ✅ | ✅ | ✅ | ✅ | 2 |
| Synopsis with expand/collapse | ✅ | ✅ | ✅ | ✅ | 17 |
| Episode list with air dates | ✅ | ✅ | ✅ | 🚧 | 25 |
| Chapter list with release dates | ✅ | ✅ | ✅ | 🚧 | 25 |
| **Characters** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Voice actors/Staff** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Producers** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Streaming/service links** (Crunchyroll, Netflix, etc.) | ✅ | ✅ | ❌ | 🔲 | **33** |
| **Trailers / YouTube videos** | ❌ | ✅ | ❌ | 🔲 | **33** |

### 2. STREAMING & PLAYBACK

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Episode player (iframe embed) | ✅ | ❌ | ❌ | 🚧 | 28 |
| Multiple server mirrors | ✅ | ❌ | ❌ | 🚧 | 28 |
| Sub/Dub toggle | ✅ | ❌ | ❌ | 🚧 | 28 |
| **Auto-next episode** | ✅ | ❌ | ❌ | 🔲 | **37** |
| **Keyboard shortcuts** (space, f, n, b) | ✅ | ❌ | ❌ | 🔲 | **37** |
| **Multiple subtitle languages** | ✅ | ❌ | ❌ | 🔲 | **37** |
| **Server reliability tracking + auto-failover** | ✅ | ❌ | ❌ | 🔲 | **37** |
| **Report broken link** | ✅ | ❌ | ❌ | 🔲 | **37** |
| **Skip intro/outro** | ✅ | ❌ | ❌ | 🔲 | **37** |
| **Picture-in-picture** | ✅ | ❌ | ❌ | 🔲 | **37** |
| **Download links** | ✅ | ❌ | ❌ | 🔲 | **37** |

### 3. DISCOVERY & BROWSE

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Search with autocomplete | ✅ | ✅ | ✅ | 🚧 | 27 |
| Trending now | ✅ | ✅ | ✅ | 🚧 | 27 |
| Popular this season | ✅ | ✅ | ✅ | 🚧 | 27 |
| Recently updated/added | ✅ | ❌ | ✅ | 🚧 | 27 |
| Genre browsing/filtering | ✅ | ✅ | ✅ | 🚧 | 27 |
| Continue Watching | ✅ | ❌ | ❌ | 🚧 | 27 |
| New Releases | ✅ | ✅ | ✅ | 🚧 | 27 |
| **Advanced browse** (year, season, format, status, score, sort) | ✅ | ✅ | ✅ | 🔲 | **36** |
| **Tags browse with relevance %** | ❌ | ✅ | ❌ | 🔲 | **36** |
| **Seasonal anime page** (current + upcoming) | ❌ | ✅ | ✅ | 🔲 | **36** |
| **Top/Charts page** (by score, popularity, favorites) | ✅ | ✅ | ✅ | 🔲 | **35** |
| **Random anime** | ✅ | ❌ | ✅ | 🔲 | **36** |
| **"More like this" recommendations** | ❌ | ✅ | ✅ | 🔲 | **36** |

### 4. TRACKING & LISTS

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Status-based lists (watching/completed/paused/dropped/plan) | ✅ | ✅ | ✅ | ✅ | 6 |
| Progress tracking (episodes/chapters) | ✅ | ✅ | ✅ | ✅ | 6 |
| Score (1-10, 0-100, star) | ❌ | ✅ | ✅ | ✅ | 6 |
| Start/end dates | ❌ | ✅ | ✅ | ✅ | 6 |
| Rewatch/reread count | ❌ | ✅ | ✅ | ✅ | 6 |
| Notes per entry | ❌ | ✅ | ✅ | ✅ | 6 |
| Custom lists | ❌ | ✅ | ✅ | ✅ | 6 |
| List entry history / activity log | ❌ | ✅ | ❌ | ✅ | 6 |
| Import from AniList/MAL | ❌ | ✅ | ✅ | 🚧 | 29 |
| **Multiple score formats** (100pt, 10pt, 5-star, smiley) | ❌ | ✅ | ❌ | 🔲 | — |
| **List views: grid / list / detailed toggle** | ❌ | ✅ | ✅ | 🔲 | **38** |
| **Batch editing list entries** | ❌ | ✅ | ❌ | 🔲 | **40** |
| **List export (JSON/CSV)** | ❌ | ✅ | ✅ | 🔲 | **40** |

### 5. USER STATISTICS

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| **Genre distribution (pie/bar chart)** | ❌ | ✅ | ✅ | 🔲 | **34** |
| **Format distribution** | ❌ | ✅ | ✅ | 🔲 | **34** |
| **Score distribution** | ❌ | ✅ | ✅ | 🔲 | **34** |
| **Yearly activity calendar (heatmap)** | ❌ | ✅ | ❌ | 🔲 | **34** |
| **Voice actor stats** (most watched VA) | ❌ | ✅ | ❌ | 🔲 | **34** |
| **Studio stats** (most watched studio) | ❌ | ✅ | ❌ | 🔲 | **34** |
| **Mean score, standard deviation** | ❌ | ✅ | ✅ | 🔲 | **34** |
| **Days/total time wasted** | ❌ | ✅ | ✅ | 🔲 | **34** |
| **Stats by year/season filters** | ❌ | ✅ | ❌ | 🔲 | **34** |

### 6. CHARACTERS & STAFF

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| **Character database** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Character page with bio, image, animeography** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Voice actor/Staff database** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Staff page with filmography** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Character list on media detail** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Staff list on media detail** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Voice actor per character per language** | ❌ | ✅ | ✅ | 🔲 | **33** |
| **Character search** | ❌ | ✅ | ✅ | 🔲 | **33** |

### 7. SOCIAL & COMMUNITY

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Friend groups | ❌ | ❌ | ❌ | ✅ | 5 |
| Activity feed (list changes) | ❌ | ✅ | ❌ | ✅ | 6/19 |
| Recommendations (user→user) | ❌ | ✅ | ✅ | ✅ | 9/19 |
| Discussions (per-title, group-scoped) | ❌ | ✅ | ✅ | ✅ | 9/19 |
| **Discussion replies with threading** | ❌ | ✅ | ✅ | ✅ | 9 |
| **Follow/friend system** (not groups) | ❌ | ✅ | ✅ | 🔲 | **38** |
| **User-to-user recommendations from media detail** | ❌ | ✅ | ✅ | 🔲 | **38** |
| **Activity feed posting** (text status, not just list changes) | ❌ | ✅ | ❌ | 🔲 | **38** |
| **Reviews on media detail** (markdown, helpful votes) | ❌ | ✅ | ✅ | 🔲 | **38** |
| **Global anime discussions** (not group-scoped) | ❌ | ✅ | ✅ | 🔲 | **38** |
| **User profiles with stats display** | ❌ | ✅ | ✅ | 🔲 | **38** |
| **Share links** (deep links to media/episode) | ❌ | ✅ | ❌ | 🔲 | **38** |

### 8. WATCH PARTY

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Watch party scheduling with RSVP | ❌ | ❌ | ❌ | ✅ | 11/20 |
| **Watch2Gether / Sync playback** | ✅ | ❌ | ❌ | 🔲 | **37** |

### 9. NOTIFICATIONS

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Notification inbox (all/unread/mark read) | ❌ | ✅ | ✅ | ✅ | 21 |
| Notification preferences | ❌ | ✅ | ✅ | ✅ | 21 |
| **New episode notifications (push/discord/telegram)** | ❌ | ✅ | ❌ | 🚧 | **30** |
| **Friend activity notifications** | ❌ | ✅ | ❌ | ✅ | — |
| **Recommendation notifications** | ❌ | ✅ | ✅ | ✅ | — |

### 10. MANGA

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Manga/manhwa metadata | ❌ | ✅ | ✅ | ✅ | 3 |
| Chapter tracking | ❌ | ✅ | ✅ | ✅ | 6 |
| MangaDex sync | ❌ | ❌ | ❌ | ✅ | 3 |
| **Manga reader** | ❌ | ❌ | ❌ | 🔲 | **39** |
| **Chapter source/mirror switching** | ❌ | ❌ | ❌ | 🔲 | **39** |
| **Reading direction (LTR/RTL/Vertical)** | ❌ | ❌ | ❌ | 🔲 | **39** |
| **Bookmark within chapter** | ❌ | ❌ | ❌ | 🔲 | **39** |

### 11. PLATFORM & UX

| Feature | AniWave | AniList | MAL | OtakuHub | Phase |
|---------|---------|---------|-----|----------|-------|
| Dark theme | ✅ | ✅ | ✅ | ✅ | 15 |
| Responsive web (mobile + desktop) | ✅ | ✅ | ✅ | ✅ | 15 |
| Continue Watching | ✅ | ❌ | ❌ | 🚧 | 27 |
| **PWA / Install prompt** | ❌ | ❌ | ❌ | 🔲 | **40** |
| **Multi-language UI (i18n)** | ❌ | ❌ | ❌ | 🔲 | **40** |
| **Theme customization** (accent color, custom CSS) | ❌ | ✅ | ❌ | 🔲 | **40** |
| **Watch history** (full session history, not just current) | ❌ | ❌ | ❌ | 🔲 | **40** |
| **List import/export (JSON/CSV)** | ❌ | ✅ | ✅ | 🔲 | **40** |
| **Keyboard navigation** (not just player) | ❌ | ✅ | ✅ | 🔲 | **37** |

---

## New Phases Required (33–40)

### Phase 33 — Characters, Staff & Voice Actors
The largest data gap. AniList has 770,000+ characters and 500,000+ staff.

**Backend:**
| Sub-phase | Task |
|-----------|------|
| 33.1 | `characters` table + model + repository (name, image, description, favorites count) |
| 33.2 | `staff` table + model + repository (name, image, description, role) |
| 33.3 | `media_characters` join table (character role: MAIN/SUPPORTING/BACKGROUND, voice actor reference) |
| 33.4 | `media_staff` join table (staff role: DIRECTOR, STORYBOARD, ANIMATION_DIRECTOR, etc.) |
| 33.5 | `character_voice_actor` join table (character ↔ staff ↔ language ↔ media_id) |
| 33.6 | AniList sync pipeline for characters and staff (new Celery task, rate-limited) |
| 33.7 | API endpoints: `GET /characters/{id}`, `GET /staff/{id}`, `GET /media/{id}/characters`, `GET /media/{id}/staff` |
| 33.8 | Character search endpoint |

**Frontend:**
| Sub-phase | Task |
|-----------|------|
| 33.9 | Character page (bio, image, animeography, voice actor roles) |
| 33.10 | Staff page (bio, image, filmography by role) |
| 33.11 | Character list tab on media detail (with voice actor names) |
| 33.12 | Staff list tab on media detail (with role labels) |
| 33.13 | Character search page |
| 33.14 | Tests |

### Phase 34 — Advanced User Statistics
AniList's most loved feature. High engagement value for a friend group — comparing stats is fun.

**Backend:**
| Sub-phase | Task |
|-----------|------|
| 34.1 | Stats computation service — genre distribution from user list entries |
| 34.2 | Format distribution, score distribution, status distribution |
| 34.3 | Yearly activity calendar (group by completed_at dates per month/day) |
| 34.4 | Voice actor / studio stats (most watched, requires Phase 33) |
| 34.5 | API endpoint: `GET /users/{id}/stats?type=genres|formats|scores|activity|studios|voice_actors` |

**Frontend:**
| Sub-phase | Task |
|-----------|------|
| 34.6 | Stats page on user profile (tab or separate page) |
| 34.7 | Genre distribution chart (HTML/CSS bar chart or lightweight chart library — no heavy deps) |
| 34.8 | Score distribution histogram |
| 34.9 | Activity calendar heatmap (GitHub-style) |
| 34.10 | Stats summary card ("N days watched", "Mean score: X", "Most watched genre") |
| 34.11 | Tests |

### Phase 35 — Charts & Top Lists

**Backend:**
| Sub-phase | Task |
|-----------|------|
| 35.1 | Top anime endpoint — `GET /charts/top?category=score|popularity|favorites|members` |
| 35.2 | Seasonal ranking endpoint |
| 35.3 | Group-specific charts (what's popular in my group) |

**Frontend:**
| Sub-phase | Task |
|-----------|------|
| 35.4 | Charts page with tab switcher (Top Rated / Most Popular / Most Favorited / Trending) |
| 35.5 | AnimeCard grid with ranking numbers |
| 35.6 | Group charts section |
| 35.7 | Tests |

### Phase 36 — Advanced Discovery & Browse

**Backend:**
| Sub-phase | Task |
|-----------|------|
| 36.1 | Enhanced browse endpoint — `GET /browse?genres=...&year=...&season=...&format=...&status=...&score_min=...&sort=...` |
| 36.2 | Tags-based discovery |
| 36.3 | Seasonal grouping endpoint (current season + next season) |
| 36.4 | Random anime endpoint |
| 36.5 | "More like this" recommendations (by shared tags/genres) |

**Frontend:**
| Sub-phase | Task |
|-----------|------|
| 36.6 | Browse page with advanced filter sidebar (genre checkboxes, year slider, format dropdown, sort selector) |
| 36.7 | Tag search page with relevance indicators |
| 36.8 | Seasonal anime page (current season grid + upcoming tab) |
| 36.9 | Random anime button (with re-roll) |
| 36.10 | "More Like This" section on media detail page |
| 36.11 | Tests |

### Phase 37 — Player Enhancements

**Frontend only** (backend playback API already in Phase 25):

| Sub-phase | Task |
|-----------|------|
| 37.1 | Auto-next episode — countdown overlay after episode completes (10s → 3s auto, cancelable) |
| 37.2 | Keyboard shortcuts: Space=play/pause, F=fullscreen, N=next, B=back, M=mute, →/←=seek ±10s |
| 37.3 | Multiple subtitle language selector (if provider returns multiple language embeds) |
| 37.4 | Server reliability tracking (track per-server error rate, auto-switch on failure) |
| 37.5 | Report broken episode link (marks episode for admin review) |
| 37.6 | Skip intro/outro buttons (requires timing data — Phase 33 episode metadata enhancement) |
| 37.7 | Picture-in-picture mode (via documentPictureInPicture API) |
| 37.8 | Download link display (if provider exposes, safe URL only) |
| 37.9 | Watch history tracking (every play session logged, not just completions) |
| 37.10 | Tests |

### Phase 38 — Social & Community Expansion

**Backend:**
| Sub-phase | Task |
|-----------|------|
| 38.1 | Follow system — `user_follows` table (follower_id, followed_id) with notifications |
| 38.2 | Reviews table — `reviews` (user_id, media_id, body, score, is_spoiler, helpful_count) |
| 38.3 | Review helpful votes — `review_votes` (user_id, review_id, vote: helpful/not) |
| 38.4 | Global discussions — remove group requirement for discussions (optional group_id) |
| 38.5 | Activity feed posting — `activity_posts` table for text status updates |
| 38.6 | Share link generation — `GET /share/{type}/{id}` returns shareable deep link |
| 38.7 | API endpoints: `GET /users/{id}/followers`, `POST /follow/{user_id}`, `GET /media/{id}/reviews`, `POST /reviews`, `POST /activity/post` |

**Frontend:**
| Sub-phase | Task |
|-----------|------|
| 38.8 | Follow/unfollow button on user profiles |
| 38.9 | Reviews tab on media detail (list reviews, create review form with markdown) |
| 38.10 | Helpful/not-helpful vote buttons on reviews |
| 38.11 | Global discussion tab on media detail (not just group-scoped) |
| 38.12 | Text status posting from profile or quick-post bar |
| 38.13 | Share button on media detail + episode — copies deep link |
| 38.14 | User profile with stats display (AniList-style layout) |
| 38.15 | Tests |

### Phase 39 — Manga Reader
Currently we only track manga chapters (progress). No reading experience.

**Backend:**
| Sub-phase | Task |
|-----------|------|
| 39.1 | MangaDex chapter content API client (fetch chapter pages) |
| 39.2 | Chapter page caching strategy (cache pages, respect MangaDex rate limits) |
| 39.3 | Source provider for manga chapters (mirror switching for chapter sources) |
| 39.4 | API endpoint: `GET /media/{id}/manga/chapters/{chapter_id}/pages` (proxied, cached) |
| 39.5 | Bookmark endpoint: `PUT /reading/bookmark` (save position within chapter) |

**Frontend:**
| Sub-phase | Task |
|-----------|------|
| 39.6 | Manga reader page — scrollable vertical layout |
| 39.7 | Page turning: long-strip scroll, left-right paged, right-left for manga |
| 39.8 | Reading direction toggle (LTR / RTL / Vertical) |
| 39.9 | Source/mirror switching for chapters |
| 39.10 | Bookmark within chapter (resume from last page) |
| 39.11 | Progress auto-save (marks chapter as read when reaching last page) |
| 39.12 | Tests |

### Phase 40 — Advanced Platform Features

| Sub-phase | Task | Type |
|-----------|------|------|
| 40.1 | PWA manifest enhancement + install prompt | Frontend |
| 40.2 | Multi-language UI (i18n) — vue-i18n integration | Frontend |
| 40.3 | Theme customization — accent color picker, custom CSS | Frontend |
| 40.4 | Watch history page — full browsing/playback history with filters | Frontend + Backend |
| 40.5 | List import/export (JSON/CSV) — `GET /lists/export`, `POST /lists/import` | Backend |
| 40.6 | Data sync to AniList (write progress back) — opt-in | Backend |
| 40.7 | Batch editing list entries (multi-select status change) | Frontend + Backend |
| 40.8 | List view toggle (grid / list / detailed) | Frontend |

---

## Updated Master Roadmap (Phases 25–40)

```
Phase 25 — Streaming Backend Infrastructure           (7.5 days)  ← FROM ADR 087
Phase 26 — Streaming UI Component Library              (8.5 days)  ← FROM ADR 087
Phase 27 — Home Page Streaming Redesign                (7.5 days)  ← FROM ADR 087
Phase 28 — Media Detail Streaming Redesign             (10 days)   ← FROM ADR 087
Phase 29 — Real AniList/MAL Import                     (3.5 days)  ← FROM ADR 087
Phase 30 — Episode Notification Pipeline               (1.5 days)  ← FROM ADR 087
Phase 31 — Admin Source Provider UI                    (5 days)    ← FROM ADR 087
Phase 32 — Migration & Cleanup                         (7.5 days)  ← FROM ADR 087
──── NEW ────
Phase 33 — Characters, Staff & Voice Actors            (12 days)   ← GAP
Phase 34 — Advanced User Statistics                    (8 days)    ← GAP
Phase 35 — Charts & Top Lists                          (5 days)    ← GAP
Phase 36 — Advanced Discovery & Browse                 (8 days)    ← GAP
Phase 37 — Player Enhancements                         (6 days)    ← GAP
Phase 38 — Social & Community Expansion                (10 days)   ← GAP
Phase 39 — Manga Reader                                (10 days)   ← GAP
Phase 40 — Advanced Platform Features                  (8 days)    ← GAP
```

**Updated total estimate: ~108 days** (Phases 25–40 combined)
**Original Phase 25–32 total: 46 days**
**New Phase 33–40 total: 67 days**

## Priority Recommendation (Tiers)

### Tier 1 — Streaming Foundation (Weeks 1–4)
> Unlocks the core "watch anime" experience

| Order | Phase | Why |
|-------|-------|-----|
| 1 | **25–26** Backend + Component Library | Everything depends on this |
| 2 | **27** Home Page | First impression |
| 3 | **28** Media Detail + Player | Core consumption flow |

### Tier 2 — Data Richness (Weeks 4–7)
> Makes the platform feel complete and authoritative

| Order | Phase | Why |
|-------|-------|-----|
| 4 | **33** Characters & Staff | Fills the biggest content gap |
| 5 | **35** Charts & Top Lists | Discovery enhancement |
| 6 | **36** Advanced Discovery & Browse | Power users need filters |

### Tier 3 — Personalization & Import (Weeks 7–9)
> Makes it YOUR platform

| Order | Phase | Why |
|-------|-------|-----|
| 7 | **29** Real Import | Onboarding — bring your list |
| 8 | **34** User Stats | Fun engagement for friend groups |
| 9 | **37** Player Enhancements | Quality-of-life for watching |

### Tier 4 — Community & Polish (Weeks 9–12)
> Social features and finishing touches

| Order | Phase | Why |
|-------|-------|-----|
| 10 | **38** Social Expansion | Reviews, follows, global discussions |
| 11 | **30** Notifications Pipeline | Completes the notification loop |
| 12 | **31** Admin Source UI | Operations tooling |
| 13 | **39** Manga Reader | New content type |
| 14 | **32** Migration & Cleanup | Pay down tech debt |
| 15 | **40** Platform Features | Polish and i18n |

## What This Means for the Codebase

### New database tables required (Phases 33–40)

Total new tables: **~8**

| Table | Phase | Purpose |
|-------|-------|---------|
| `characters` | 33 | Character entries |
| `staff` | 33 | Staff/person entries |
| `media_characters` | 33 | Character roles in media |
| `media_staff` | 33 | Staff roles in media |
| `character_voice_actors` | 33 | Voice actor per character per language |
| `reviews` | 38 | User-written media reviews |
| `review_votes` | 38 | Helpful/not votes on reviews |
| `activity_posts` | 38 | Text status posts (not list changes) |
| `user_follows` | 38 | Follow/friend relationships |
| `reading_bookmarks` | 39 | Manga reading position |

### New external API clients

| Client | Phase | Purpose |
|--------|-------|---------|
| `external/anilist_character_client.py` | 33 | Fetch character/staff data from AniList GraphQL |
| `external/mangadex_chapter_client.py` | 39 | Fetch manga chapter page images from MangaDex |

## Consequences

**Good**:
- Complete feature parity with major anime platforms across streaming, tracking, and community
- Phase ordering ensures streaming works first, then data richness, then community
- No architectural contradictions — all new phases fit the existing FastAPI/Vue pattern
- Characters and staff data can be synced from AniList (they have a GraphQL API for it)

**Bad**:
- ~108 days of work remaining (full-time solo developer: ~5 months)
- Multiple new database tables require Alembic migrations and model files
- Manga reader (Phase 39) requires proxying chapter images — bandwidth and caching concerns
- Stats computation (Phase 34) needs efficient queries for large datasets

**Neutral**:
- Existing tests (187 frontend, 324 backend) provide safety net throughout
- Each phase is independently shippable — platform improves with every completed phase
- Lower-priority phases can be deferred indefinitely without breaking core functionality
