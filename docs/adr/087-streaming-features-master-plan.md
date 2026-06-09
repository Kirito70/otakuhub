# ADR 087 — Streaming Features Master Plan

**Status**: Proposed
**Date**: 2026-06-08

## Context

Multiple ADRs have been written covering individual aspects of the anime streaming experience:

| ADR | Title | Status |
|-----|-------|--------|
| 079 | Frontend Design Direction: Streaming-First UX | Proposed |
| 080 | Playback API & Episode Resolution Contract | Proposed |
| 081 | Frontend Player Architecture | Proposed |
| 082 | Media Detail Page: Streaming-First Redesign | Proposed |
| 083 | Home Page: Streaming-First Redesign | Proposed |
| 084 | Real AniList/MAL List Import | Proposed |
| 085 | Episode Notification Pipeline (Complete) | Proposed |
| 086 | Admin Source Provider UI | Proposed |

This ADR ties everything together into a prioritized roadmap with phases, dependencies, and estimated effort.

## Master Roadmap

```
Phase 23 — Streaming Infrastructure (backend)
  ├── 23.1  Playback API endpoints
  ├── 23.2  AniList/MAL real import (username-based)
  ├── 23.3  Episode notification pipeline (hook + delivery)
  └── 23.4  Apprise client enhancement

Phase 24 — Streaming UI Components (frontend custom library)
  ├── 24.1  Design token system (palette, typography, spacing)
  ├── 24.2  AnimeCard + AnimeGrid primitives
  ├── 24.3  HeroBanner + ScoreRing
  ├── 24.4  EpisodeList + ServerSelector
  └── 24.5  VideoPlayer + usePlayerListener

Phase 25 — Home Page (streaming redesign)
  ├── 25.1  HomePage layout + sections
  ├── 25.2  TrendingCarousel
  ├── 25.3  Continue Watching section
  ├── 25.4  Search integration + genre pills
  └── 25.5  Test coverage

Phase 26 — Media Detail Page (streaming redesign)
  ├── 26.1  Hero + episode list tab
  ├── 26.2  Info tab + Related tab
  ├── 26.3  Player overlay integration
  ├── 26.4  Progress tracking from player events
  └── 26.5  Test coverage

Phase 27 — Admin Source Provider UI
  ├── 27.1  Source mapping list + filters
  ├── 27.2  Sync trigger controls
  └── 27.3  Reconciliation workflow

Phase 28 — Migration & Cleanup
  ├── 28.1  Convert MyListPage to custom components
  ├── 28.2  Convert social/watchparty pages
  ├── 28.3  Strip unused Quasar components from final bundle
  └── 28.4  Full visual QA + accessibility pass
```

## Dependency Graph

```
Phase 23 (backend) ──────────────────────────────┐
  ├── 23.1 ── needed by ──→ Phase 26 (media detail) │
  ├── 23.2 ── needed by ──→ ImportListPage (done)    │
  └── 23.3 ── independent                             │
                                                     │
Phase 24 (components) ── needed by ──→ Phase 25, 26 │
  (no backend deps, can start immediately)            │
                                                     │
Phase 25 + 26 ── need both Phase 23 + 24 to be done  │
  └── but can start skeleton before backend is ready  │
                                                     │
Phase 27 ── independent from 23–26, but needs 24     │
  (for component library)
```

## Effort Estimates

| Phase | Sub-phases | Backend days | Frontend days | Test days | Total days |
|-------|-----------|-------------|--------------|----------|-----------|
| 23.1 | Playback API | 1 | 0 | 0.5 | 1.5 |
| 23.2 | Real import | 2 | 0.5 | 1 | 3.5 |
| 23.3 | Notification pipeline | 1 | 0 | 0.5 | 1.5 |
| 23.4 | Apprise enhancement | 0.5 | 0 | 0.5 | 1 |
| **23 total** | | **4.5** | **0.5** | **2.5** | **7.5** |
| 24.1 | Design tokens | 0 | 0.5 | 0 | 0.5 |
| 24.2 | AnimeCard + Grid | 0 | 1 | 0.5 | 1.5 |
| 24.3 | HeroBanner + ScoreRing | 0 | 1 | 0.5 | 1.5 |
| 24.4 | EpisodeList + ServerSelector | 0 | 1.5 | 0.5 | 2 |
| 24.5 | VideoPlayer + listener | 0 | 2 | 1 | 3 |
| **24 total** | | **0** | **6** | **2.5** | **8.5** |
| 25.1 | HomePage skeleton | 0 | 1 | 0.5 | 1.5 |
| 25.2 | TrendingCarousel | 0 | 1 | 0.5 | 1.5 |
| 25.3 | Continue Watching | 0 | 0.5 | 0.5 | 1 |
| 25.4 | Search + genres | 0.5 | 1 | 0.5 | 2 |
| 25.5 | Test coverage | 0 | 0 | 1.5 | 1.5 |
| **25 total** | | **0.5** | **3.5** | **3.5** | **7.5** |
| 26.1 | Hero + episodes | 0 | 2 | 1 | 3 |
| 26.2 | Info + Related tabs | 0.5 | 1 | 0.5 | 2 |
| 26.3 | Player overlay | 0 | 1.5 | 0.5 | 2 |
| 26.4 | Progress tracking | 0 | 0.5 | 0.5 | 1 |
| 26.5 | Test coverage | 0 | 0 | 2 | 2 |
| **26 total** | | **0.5** | **5** | **4.5** | **10** |
| 27.1 | Source mapping list | 0.5 | 1 | 0.5 | 2 |
| 27.2 | Sync triggers | 0 | 0.5 | 0.5 | 1 |
| 27.3 | Reconciliation | 0.5 | 1 | 0.5 | 2 |
| **27 total** | | **1** | **2.5** | **1.5** | **5** |
| 28.1 | MyListPage migration | 0 | 1 | 1 | 2 |
| 28.2 | Social/watchparty migration | 0 | 2 | 1 | 3 |
| 28.3 | Bundle cleanup | 0 | 0.5 | 0 | 0.5 |
| 28.4 | Visual QA | 0 | 1 | 1 | 2 |
| **28 total** | | **0** | **4.5** | **3** | **7.5** |

**Grand total: ~46 days** (approx 6–7 weeks with one developer, 3–4 weeks with two)

## Priority Recommendations

### Tier 1 — Foundation (highest value, unblocks everything else)
> **Order**: 23.1 → 24.1 → 24.2 → 24.3 → 24.4 → 24.5

| Order | Phase | Why first |
|-------|-------|-----------|
| 1 | **23.1** Playback API | Frontend needs data — this is the pipe |
| 2 | **24.1** Design tokens | Must agree on colors/typography before building components |
| 3 | **24.2–24.5** Component library | All streaming UI is built from these primitives |

### Tier 2 — User-facing features
> **Order**: 25.1→25.2→25.3→25.4→25.5 → 26.1→26.2→26.3→26.4→26.5

| Order | Phase | Why |
|-------|-------|-----|
| 4 | **25.x** Home Page | First thing users see — makes or breaks first impression |
| 5 | **26.x** Media Detail | Where users consume content — core flow |

### Tier 3 — Complementary features
> **Order**: 23.2 → 23.3 → 23.4 → 27.x

| Order | Phase | Why |
|-------|-------|-----|
| 6 | **23.2** Real import | Users can bring their existing lists — high value |
| 7 | **23.3/23.4** Notifications | Episodic notifications complete the tracking experience |
| 8 | **27.x** Admin UI | Only admins see this — lower priority |

### Tier 4 — Cleanup
| Order | Phase | Why |
|-------|-------|-----|
| 9 | **28.x** Migration | Final polish after all features are built |

## Key Design Decisions Summary

| Decision | ADR | Choice |
|----------|-----|--------|
| Frontend framework | 079 | Keep Quasar for shell; custom components for streaming UI |
| Playback API | 080 | New endpoints: `/media/{id}/sources`, `/media/{id}/episodes/sources` |
| Player architecture | 081 | Composable-based (usePlayerListener), overlay iframe, Pinia for cross-component state only |
| Media detail layout | 082 | Hero banner with cover, tabs (Episodes/Info/Related), server/language selector |
| Home page layout | 083 | Sections: Spotlight, Continue Watching, Trending, Recent Updates, Friends Activity, Genres |
| Import method | 084 | Phase 1: username-based AniList public list import (no OAuth) |
| Notification pipeline | 085 | Hook process_new_episodes into daily refresh → Apprise delivery → weekly cleanup |
| Admin source UI | 086 | Single page: trigger syncs, view jobs, reconcile unmatched mappings |

## Full Feature Landscape (Gap Analysis)

This plan covers the streaming-first redesign. However, a comprehensive gap analysis (see ADR 088) comparing OtakuHub against AniWave, AniList, and MyAnimeList reveals **8 additional phases** (33–40) required for full feature parity:

| Missing Area | Gap ADR Phase | Effort |
|-------------|---------------|--------|
| Characters, Staff & Voice Actors | 33 | 12 days |
| Advanced User Statistics | 34 | 8 days |
| Charts & Top Lists | 35 | 5 days |
| Advanced Discovery & Browse | 36 | 8 days |
| Player Enhancements | 37 | 6 days |
| Social & Community Expansion | 38 | 10 days |
| Manga Reader | 39 | 10 days |
| Advanced Platform Features | 40 | 8 days |

**Combined estimate (Phases 25–40): ~108 days** (5 months solo, ~2.5 months with two devs)

## De-scoped / Future Items

- **MAL OAuth import**: Phase 2 after AniList username import is stable (Phase 29)
- **Chromecast / AirPlay**: Requires separate provider integration (Phase 37 extension)
- **Synchronized watch parties (SyncParty / Rave)**: ADR 081 player extension
- **Download tracking**: Requires separate security contract
- **Native mobile apps**: Electron/Capacitor deployment deferred until web streaming is stable
