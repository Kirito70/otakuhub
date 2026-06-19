OtakuHub — Design System & UI Specification


For the implementing agent (Claude Code / OpenCode): This is the authoritative
visual and interaction specification for OtakuHub's Flutter app. Read it fully before
touching UI code. Implement the design tokens first (Section 2), then the component
library (Section 4), then screens (Section 6). Every screen must be built from the
shared components — never one-off styling. Where the design needs data the current API
doesn't expose, Section 8 lists the new endpoints to add; build those alongside the UI.

Aesthetic north star: cinematic, dark, poster-forward, and quietly alive — the energy
of a premium streaming app, but structured around a small group of friends, not a faceless
public catalogue. The artwork is the hero; the chrome recedes. This is an original design —
do not replicate any existing site's exact layout, logo, or component shapes.




1. Design Principles


Content is the interface. Cover art and banners carry the visual weight. UI chrome is
dark, minimal, and gets out of the way. Never put a solid color block where artwork could be.
Dark-first, always. This is a binge-at-night app. The dark theme is the primary theme,
designed first. A light theme is optional and secondary.
Calm, not flashy. Motion is purposeful — things ease in, lift on hover, cross-fade. No
bouncing, no spinning, no gratuitous parallax. Restraint reads as premium.
The group is present. Friends' faces, activity, and recommendations are woven throughout,
not hidden in a separate tab. You should feel your friends in the app constantly.
One tap to the thing. The most common action on any screen (update progress, add to list,
open detail) is always reachable in a single tap, never buried in a menu.
Every state is designed. Loading, empty, error, and offline states are first-class — never
a bare spinner or a blank screen. Skeletons mirror the real layout.
Touch and pointer both. The same code targets phones, tablets, desktop (mouse hover), and
web. Hover states enhance; they're never required to reach functionality.



2. Design Tokens

Implement these as a central AppTokens / AppColors / AppTypography set (see Section 9 for the
Flutter ThemeData wiring). Never hardcode a hex value in a widget — always reference a token.

2.1 Color — Dark Theme (primary)

Surfaces (layered depth — darker = further back):

TokenHexUsebg.base#0B0B12App background (near-black, faint violet-blue tint)bg.surface#14141FCards, list rowsbg.surfaceAlt#1A1A28Inputs, secondary cardsbg.elevated#1F1F30Modals, bottom sheets, menusbg.hover#26263AHover/pressed surface tintborder.subtle#262636Hairline dividers, card borders (1px)border.strong#3A3A52Focused inputs, emphasized edges

Text:

TokenHexUsetext.primary#F4F4F8Titles, primary contenttext.secondary#A6A6BDSubtitles, metadatatext.tertiary#6E6E85Hints, timestamps, disabled-ishtext.onAccent#0B0B12Text sitting on a bright accent fill

Brand & accents:

TokenHexUseaccent.primary#7C5CFCBrand violet — primary buttons, active nav, linksaccent.primaryHover#8E72FFHover stateaccent.primaryPressed#6A48E0Pressed stateaccent.primarySubtle#7C5CFC @ 14% alphaTinted backgrounds behind violet elementsaccent.coral#FF6E8AHighlights, "new", live dots, secondary CTAaccent.mint#2FD9A8Progress, "watching", successaccent.sky#5AB0FFInfo, "plan to watch", links in bodyaccent.amber#FFB454Warnings, "paused", airing-soonaccent.rose#FF5C6CErrors, "dropped", destructive

Brand gradient (use sparingly — FAB, hero CTA, achievement, logo accent):
linear-gradient(135°, #7C5CFC → #FF6E8A) (violet → coral).

Watch-status color map (one hue per status — used on chips, list rails, progress bars):


watching → mint #2FD9A8
rewatching → #3FD0D9 (cyan)
completed → accent.primary #7C5CFC
plan to watch / read → sky #5AB0FF
paused / on hold → amber #FFB454
dropped → rose #FF5C6C


Score color scale (for the rating chip — color the number by value):


8.5–10 → mint
7.0–8.4 → #7FD957 (green)
5.5–6.9 → amber
< 5.5 → rose
unrated → text.tertiary


2.2 Color — Light Theme (secondary, optional)

Build only after dark is complete. Same token names, remapped:
bg.base #F7F7FB, bg.surface #FFFFFF, bg.elevated #FFFFFF, border.subtle #E6E6EF,
text.primary #15151F, text.secondary #5A5A70, accents unchanged but use the pressed
variants for text-on-light contrast. Cover art looks worse on light backgrounds, so dark
remains the recommended default and the onboarding default.

2.3 Typography

Use google_fonts. Three families:


Display — Space Grotesk — hero titles, big numbers, section headers with personality.
UI / Body — Plus Jakarta Sans — everything else. Clean, geometric, excellent at small sizes.
Native titles — Noto Sans JP — Japanese/Korean/Chinese original titles (auto-fallback).


Two weights only across the app: 400 (regular) and 600 (semibold). (Display may use 700 for hero numbers.)

StyleFontSize / LineWeightUsedisplayXLSpace Grotesk40 / 46700Hero spotlight title (desktop)displayLSpace Grotesk30 / 36700Hero title (mobile), big stat numbersheadlineLSpace Grotesk24 / 30600Screen titlestitleLPlus Jakarta20 / 26600Section headers ("Continue watching")titleMPlus Jakarta17 / 22600Card titles, dialog titlesbodyLPlus Jakarta15 / 22400Primary body, synopsisbodyMPlus Jakarta14 / 20400Secondary text, metadatalabelPlus Jakarta13 / 16600Buttons, tabs, chipscaptionPlus Jakarta12 / 16400Timestamps, footnotesmicroPlus Jakarta11 / 14600Badges, status pills, counters

Always sentence case. Never ALL CAPS except a single-letter rank/badge.

2.4 Spacing, Radius, Layout

Spacing scale (4pt base): 4, 8, 12, 16, 20, 24, 32, 40, 56, 72. Use space.md = 16 as the
default gutter. Screen edge padding: 16 (mobile), 24 (tablet), 40 (desktop).

Radius: sm 10, md 14, lg 20, xl 28, pill 999. Cards use lg (20). Poster cards md (14).
Buttons pill for primary CTAs, md for secondary. Bottom sheets xl top corners only.

Elevation (dark UI = use surface lightening + soft shadow, not heavy drop shadows):


e0 flat (base)
e1 cards: surface bg.surface + shadow 0 2 8 rgba(0,0,0,0.35)
e2 raised/hover: surface bg.elevated + shadow 0 8 24 rgba(0,0,0,0.45)
e3 modals/sheets: surface bg.elevated + shadow 0 16 48 rgba(0,0,0,0.55)


Breakpoints: compact < 600 (phone), medium 600–1024 (tablet / small window),
expanded > 1024 (desktop / web). Use LayoutBuilder + a single Responsive helper.

2.5 Imagery & Posters


Poster aspect ratio: 2:3 (standard anime cover). Always 2:3, never letterbox a poster.
Banner aspect ratio: 16:9 desktop, 3:2 mobile hero crop.
All remote images via cached_network_image with: a shimmer skeleton placeholder of the exact
final size, and an error fallback (dark surface + centered ti-photo-style icon + title text).
Poster corner radius md (14), clipped. Subtle 1px border.subtle inside edge to separate dark
posters from dark background.
Lazy-load offscreen images. Decode at display size, not full size.



3. Motion & Interaction

Durations: instant 90ms, fast 160ms, base 240ms, slow 360ms.
Curves: default Curves.easeOutCubic; entrances easeOutQuart; exits easeInCubic.

Use the flutter_animate package for declarative entrances.

InteractionSpecPoster card hover (pointer)scale 1.0 → 1.04, shadow e1 → e2, reveal title+score overlay, fastPoster card press (touch)scale 1.0 → 0.97, instant, release springs backPage transitionshared-axis horizontal (push) / fade-through (tab switch), baseBottom sheetslide up + scrim fade, base, easeOutQuartList item entrancestaggered fade + 12px slide-up, 40ms stagger, first paint onlyProgress +1 tapnumber rolls up (AnimatedSwitcher), mint ring pulses once, fastSkeleton shimmer1.2s loop, diagonal sweep, bg.surfaceAlt → bg.hoverTab indicatorslides under active tab, fast, accent.primaryFABgradient, on scroll-down it shrinks to icon-only, scroll-up expands w/ labelPull to refreshcustom indicator: a small spinning ring in accent.primary, not stock Material

Honor MediaQuery.disableAnimations / reduce-motion: cut durations to instant and drop slides.


4. Component Library

Build each as a reusable widget in lib/core/widgets/. Screens compose these only.

4.1 PosterCard

The atom of the whole app. Used in every grid and rail.


2:3 cached image, radius md, 1px inner border.
Resting (touch): image only, with a small score chip (top-right) and a thin status rail
(bottom, 3px, colored by watch status if the title is in the user's list).
Hover (pointer): dark gradient scrim rises from bottom; shows title (titleM, 2-line clamp),
format + year (caption), and a circular +/progress quick-action button.
Long-press (touch): opens the Quick-Action sheet (4.7).
Sizes: sm (w104), md (w140), lg (w168). Rails use md; grids use responsive md/lg.


4.2 ScoreChip


Pill, bg = score color @ 16% alpha, text = score color, micro weight.
Shows ★ 8.7. If unrated, hollow star + – in text.tertiary.


4.3 StatusPill


Pill colored by watch-status map. Label = status name. Optional leading 6px dot.
Used on list rows, detail page, feed items.


4.4 ProgressControl


Inline episode/chapter stepper: –  Ep 5 / 12  +.
+/– are circular 32px tap targets. Center is tappable → opens number-pad sheet for direct set.
On +: optimistic update, number rolls, a mint ring pulses. On API failure: revert + toast.
A thin progress bar under it (mint fill) when maxProgress is known.


4.5 SectionHeader


titleL left, optional "See all →" text button right (accent.primary).
Optional leading accent bar (3px × 18px, accent.primary) for emphasis on key sections.


4.6 ContentRail


Horizontal scrolling row of PosterCards with a SectionHeader above.
Snap-to-card scroll on touch; arrow buttons on hover (desktop). Edge fade-out gradient.
First card left-aligned to screen padding; trailing peek of next card to signal scrollability.


4.7 QuickActionSheet (bottom sheet)


Triggered by long-press on any PosterCard or the + on detail.
Header: mini poster + title. Then: status selector (segmented, colored), ProgressControl,
ScoreWidget (QRating-style, 10 half-stars), "Recommend to a friend" row, "Add to custom list" row.
Radius xl top, e3, drag handle. Saves on dismiss (debounced) with a confirmation toast.


4.8 FriendAvatar


Circular avatar with a 2px ring. Ring color = accent.mint if active in last 5 min, else transparent.
Fallback: initials on a deterministic color from the brand ramp. Stackable (AvatarStack) for
showing "3 friends watching this" with +N overflow.


4.9 AppButton


primary: pill, gradient or solid accent.primary, text.onAccent, label weight, 44px tall.
secondary: pill, bg.surfaceAlt, text.primary, 1px border.subtle.
ghost: text only, accent.primary.
destructive: solid accent.rose.
All: press scale 0.98, disabled at 38% opacity, loading shows inline ring (no label shift).


4.10 AppChip / FilterChip


Pill, bg.surfaceAlt, selected = accent.primarySubtle bg + accent.primary text + 1px border.
Used for genre filters, format filters, sort options.


4.11 EmptyState


Centered: a simple line illustration or large outline icon (text.tertiary), a titleM line,
a bodyM subtitle, and an optional primary action. One per empty screen — never a blank page.


4.12 Skeletons


PosterCardSkeleton, RailSkeleton, ListRowSkeleton, DetailSkeleton, FeedItemSkeleton.
Each mirrors the real component's dimensions exactly. Shimmer per 3.x.


4.13 Toast / Snackbar


Bottom-floating, bg.elevated, radius lg, e3. Leading status icon. Optional "Undo" action
(accent.primary) — required for destructive actions (remove from list, delete). Auto-dismiss 4s.


4.14 NavigationScaffold


Compact: bottom nav bar (5 items: Home, Search, My List, Feed, You). Floating, bg.elevated,
radius xl, sits 12px above the bottom edge with a blur backdrop. Active item: icon + label +
accent.primary; inactive: icon only, text.tertiary.
Medium: NavigationRail, collapsed (icons), left edge.
Expanded: extended NavigationRail (icons + labels) + a top bar with search and avatar.
Notification bell with a coral count badge lives top-right (medium/expanded) or as the 5th item's
badge (compact, on "You").



5. Information Architecture & Navigation

Primary destinations (bottom nav / rail):


Home — personalized landing (spotlight, continue, friend activity, recommendations, trending).
Search / Discover — search + browse by genre/season/format.
My List — the user's tracking library (tabbed by status).
Feed — the social heart: friend activity, recommendations inbox, discussions.
You — profile, stats, watch parties, notifications, settings, group management.


Secondary (pushed routes): Media Detail, Friend Profile, Discussion Thread, Watch Party Detail,
Airing Calendar, Import, Custom List Detail, Group Management, Settings sub-pages.

Use go_router named routes (already in the architecture). Deep links: otakuhub://media/{id},
otakuhub://party/{id}, otakuhub://group/join/{code}.


6. Screen-by-Screen Design

For each screen: layout, key components, responsive notes, and states. Build mobile-first, then
adapt at breakpoints.

6.1 Onboarding & Auth


Splash: full-bleed dark with the OtakuHub wordmark (gradient accent) center, subtle logo
fade-in. Routes to Home (if token) or Welcome.
Welcome: a slow, dimmed collage of poster art behind a dark scrim; wordmark + one-line value
prop ("Track anime with the people you actually watch with"); Log in (primary) and
Create account (secondary).
Login / Register: single centered card (e2, max width 420 on desktop). Inputs are
bg.surfaceAlt, radius md, with floating labels and inline validation (rose text). Primary
button full-width. "Join with invite code" link below.
Join group: invite-code input or auto-filled from deep link; shows the group's name + avatar

member stack before confirming.



States: loading button ring; error banner above the form (rose, dismissible).


6.2 Home

The flagship screen. Vertical scroll of horizontal rails over a hero.


Spotlight hero (top): full-width 16:9 (desktop) / 3:2 (mobile) banner of one standout
title — chosen by the group's collective taste (see endpoint 8.1). Dark gradient scrim bottom-left
holds: format/score/year row, displayL title, 2-line synopsis clamp, and two buttons —
+ Add to list (primary) and Details (secondary). On desktop, a row of 3–5 small dot indicators
cycles spotlight titles every ~8s (pauses on hover); on mobile it's a swipeable pager.
"Jump back in" rail: Continue watching — titles with status=watching, each PosterCard shows
a mint progress bar and "Ep 6 / 12 →"; tapping the card resumes (opens detail at the next ep).
"From your friends" rail: recommendations friends sent you (PosterCards with the recommender's
FriendAvatar overlapping the corner). Empty → EmptyState nudging you to ask a friend.
"Your group is watching" rail: what friends are actively watching now, AvatarStack on each card.
"Airing soon" rail: next episodes for titles in your list, each card with an amber countdown chip.
"Trending in your group" rail / "Because you liked X" rail: discovery.
Pull-to-refresh re-fetches the whole home composite. Skeleton: hero block + 3 rail skeletons.
Responsive: desktop shows a taller hero and 6 cards per rail; mobile shows hero + ~2.3 cards peeking.


6.3 Search / Discover


Search bar pinned top (bg.surfaceAlt, pill, leading search icon, clear button). Debounced 300ms.
Before typing: browse mode — filter chips (Anime / Manga / Manhwa), then rails: "By genre"
(genre chips that filter), "This season", "Top rated all time".
While typing: results as a responsive poster grid (2 cols mobile → 6 cols desktop). Each
result card shows score + format. Sticky filter/sort bar appears (sort: relevance, score, popularity,
newest; filter: type, genre, status, year).
States: empty query → browse mode; no results → EmptyState ("No titles match — try fewer
filters"); loading → grid of PosterCardSkeletons.


6.4 Media Detail

The richest screen. Scrollable, immersive.


Header: full-width banner (16:9/3:2) with a dark gradient scrim. The poster floats,
overlapping the banner's bottom edge (left on desktop, centered-left on mobile). Beside/under it:
romaji title (headlineL), native title (bodyM, Noto Sans JP, text.secondary), and a meta row
(format · episodes · season year · ScoreChip).
Primary action bar (sticky-ish): if not in list → + Add to list (primary, opens QuickActionSheet).
If in list → a compact StatusPill + inline ProgressControl + a ⋯ for more. Plus Recommend
(coral ghost) and a Discuss button with a reply-count badge.
Synopsis: bodyL, expandable (3-line clamp → "Read more"). Genre chips below.
"In your group" strip: AvatarStack + line like "Maya & 2 others completed this · avg 8.4" →
taps through to who/how they rated it. This is the social differentiator — make it prominent.
Details grid: studios, source, status, aired dates, duration — two-column key/value list.
Episodes / Chapters: for anime, a list of episodes with air dates and a "watched up to here"
marker; tapping sets progress. For manga, chapter list with published dates (MangaDex data).
Relations rail: sequels/prequels/side stories as PosterCards (relation labeled).
Recommendations rail: "More like this".
Discussion preview: top 2 threads from the group + "View all discussions →".
Where to watch: a row of outbound source chips (the user's pinned source first). Opens external.
Skeleton: banner block + poster + title lines + action bar + 2 rail skeletons.


6.5 My List


Tabs: Watching · Reading · Completed · Plan · Paused · Dropped (scrollable tab bar, indicator
in accent.primary). A count badge per tab.
View toggle: grid (PosterCards) or list (ListRow: thumb + title + StatusPill + ProgressControl +
score). Default to list on mobile (denser, faster progress updates), grid on desktop.
Per-row quick progress: the ProgressControl is inline — updating is one tap, no navigation.
Sort/filter bar: sort by last updated, title, score, progress; filter by format, genre.
Header summary (collapsible): small stat row — "142 completed · 1,240 episodes · 38 days watched".
Swipe actions (mobile): swipe a row for quick status change / remove (with Undo toast).
States: empty tab → EmptyState with a CTA ("Find something to watch" → Search).


6.6 Feed (social hub)

Three sub-tabs: Activity, Recommendations, Discussions.


Activity: reverse-chron list of FeedItems. Each: FriendAvatar + name, an action sentence
("started watching", "rated 9", "reached Ep 12 of", "completed"), a mini poster, and a relative
time. Group selector at top if in multiple groups. Tapping a poster → detail; tapping a name →
profile. Infinite scroll. Optionally group consecutive same-user events ("Maya logged 4 episodes").
Recommendations: inbox of titles friends sent you — cards with recommender avatar + their note,
Add to list (adds + acknowledges) and Dismiss. A "Sent" toggle shows ones you've sent.
Discussions: list of active threads across the group (title, anime thumb, author, reply count,
episode tag, last-activity time). FAB to start a thread.
States: quiet group → EmptyState ("It's quiet — recommend something to get things going").


6.7 Discussion Thread


Header: the anime mini-card + thread title + episode/spoiler tags.
Posts as chat-style bubbles (yours right-aligned, others left with FriendAvatar). Spoiler-tagged
text renders blurred with a "Tap to reveal" overlay until tapped.
Composer pinned bottom: text field + spoiler toggle + episode-tag selector + send.
Threaded replies indent one level (keep it shallow). Long-press a post → react / reply / report.


6.8 Friend Profile


Header card: large FriendAvatar, display name, "@username", member-since, and a Recommend to them
button. Active-ring if online.
Stat row: watching / completed / mean score / estimated days — as big-number cards (displayL).
Taste snapshot: top genres as chips sized by frequency; a small "favorites" poster rail.
Recent activity list (their last ~20 events).
"Compatibility" flourish (optional, nice-to-have): a single % derived from shared completed titles
and score correlation — render as a ring with a one-line caption.


6.9 Watch Party


List: upcoming parties as wide cards — anime banner strip, title + episode, date/time, a
countdown chip, an AvatarStack of attendees, and the user's RSVP state. Past parties dimmed below.
Create: stepper-lite single sheet — pick title (search), episode, date/time picker, optional
stream URL + sync URL, note. Primary Schedule.
Detail: big countdown (rolls down live), attendee list split into Going / Declined / Invited,
RSVP segmented control, Open stream button (gradient, prominent near start time), and a small
in-party chat reusing the discussion composer.
Within 15 min of start: the card/detail surfaces a pulsing coral "Live soon" indicator.


6.10 Airing Calendar


Sectioned vertical list grouped by day (Today, Tomorrow, Wed…). Each row: time, anime thumb, title,
episode number, countdown chip (amber if <24h). A "subscribe to calendar (.ics)" action top-right.
Optional week-grid view on desktop (7 columns, episodes as chips in day columns).


6.11 Notifications


Grouped by date. Each NotificationItem: a type icon in a tinted circle (episode=mint, chapter=sky,
rec=coral, party=violet, social=amber), bold title, body, relative time. Unread rows have a faint
accent.primarySubtle wash + a leading dot. "Mark all read" top-right. Tapping routes to the source.
Preferences (sub-page): per-type toggles, plus delivery channels — Discord webhook field,
Telegram chat ID, email/push toggles. Test-send button per channel.


6.12 You / Profile & Settings


Your own profile (as 6.8 but editable: avatar, display name, bio, timezone).
Quick links: Watch parties, Airing calendar, Import list, Custom lists, Group management, Notifications.
Settings: theme (dark/light/system — default dark), default landing tab, spoiler-blur on/off,
list privacy defaults, account (change password, log out, delete account), about.
Group management: group name/avatar, the invite code as a big copyable block + share, member list
with roles + last-seen, leave group (destructive, confirm + Undo).



7. States, Accessibility, Edge Cases


Loading: always skeletons that match layout; never a centered spinner on a full screen
(spinners are only for in-button and pull-to-refresh).
Empty: every list/grid/tab has a tailored EmptyState with a CTA.
Error: inline error card with a Retry button; network errors show an offline banner. Never a
raw exception string — map to friendly copy.
Offline: show cached data with a subtle "Offline — showing saved data" top banner; queue
progress updates and sync on reconnect (optimistic UI already updated locally).
Accessibility: every interactive element ≥ 44×44 tap target; semantic labels on icon buttons;
text scales with system font size (test up to 130%); maintain ≥ 4.5:1 contrast for body text
(the token set is designed to pass on bg.base); honor reduce-motion; full keyboard/focus support
on web/desktop (visible focus ring = 2px accent.primary). Spoiler content must be reachable but
never auto-revealed.
Localization-ready: all strings via l10n ARB; never concatenate sentences (use placeholders)
so the activity-feed phrasing can translate.



8. New / Adjusted API Endpoints the Design Requires

Build these alongside the UI (follow the existing FastAPI layered pattern). Each is a thin
aggregation/optimization over data we already store — no new external sources.

8.1 GET /api/v1/home  — composite home payload (one round trip)

Returns everything Home needs so the screen makes a single call:

jsonc{
  "spotlight": [ MediaSummary + bannerImage ],        // 3–5 group-relevant standouts
  "continue_watching": [ ListEntrySummary + nextEpisode ],
  "friend_recommendations": [ Recommendation + Media + fromUser ],
  "group_watching_now": [ Media + [friendAvatars] ],
  "airing_soon": [ Media + nextAiringEpisode ],       // titles in user's list
  "trending_in_group": [ MediaSummary ],
  "because_you_liked": { "seed": Media, "items": [ MediaSummary ] }
}

Spotlight selection logic: highest group mean-score among recently-active or currently-airing titles,
deduped against what the user has already completed. Cache per-group for ~15 min.

8.2 GET /api/v1/lists/me/continue  — continue-watching feed

Status=watching, ordered by most recent progress activity; includes next_episode and air status.
(Can be folded into 8.1 but expose standalone for the My List "resume" affordance.)

8.3 GET /api/v1/media/{id}/group-context  — the social strip on detail

jsonc{
  "in_list_count": 4,
  "completed_count": 2,
  "group_mean_score": 8.4,
  "members": [ { user, status, score, progress } ],   // who in the group has it & their state
  "recommended_by": [ user ]                            // friends who recommended it to anyone
}

8.4 GET /api/v1/media/browse  — discover browse rails

Query params: by=genre|season|top|trending, plus genre, season, year, media_type, cursor.
Powers Search's pre-typing browse mode and the genre filter rails.

8.5 GET /api/v1/users/{username}/stats  — profile stat cards

jsonc{
  "watching": 12, "completed": 142, "mean_score": 7.9,
  "episodes_watched": 1240, "days_watched": 38.2,
  "top_genres": [ { "name": "Action", "count": 51 } ],
  "favorites": [ MediaSummary ]                         // user-pinned or top-scored
}

8.6 GET /api/v1/users/{username}/compatibility  — optional taste-match

Returns { "percent": 78, "shared_completed": 23, "based_on": "score correlation" } for the profile
flourish. Compute from overlapping completed titles + Pearson correlation of scores.

8.7 GET /api/v1/social/feed?group_id=&group_consecutive=true  — grouped activity

Extend the existing feed to optionally collapse consecutive same-user progress events into one item
("logged 4 episodes of One Piece") to keep the feed readable. Add cursor pagination if not present.

8.8 POST /api/v1/media/{id}/source-preference  — pinned "where to watch"

Stores the user's preferred external source per title (or globally) so the detail page can surface it
first. { "source": "crunchyroll" | "custom", "url": "..." }. Plus GET to read it back.

8.9 Field additions to existing responses


MediaSummary everywhere should include banner_image, format, season_year, average_score,
and the caller's user_entry (status + progress) so PosterCards can render status rails without a
second call.
Activity/feed items should include the actor's avatar_url + display_name inline.
Airing endpoints should include a precise airing_at timestamp for the countdown chips.



If any of these conflict with the current docs/api-spec.md, prefer extending existing endpoints
over adding new ones, and update docs/api-spec.md + docs/database-schema.md accordingly (the
source-preference and favorites features may need a small table/column — design a migration).




9. Flutter Implementation Notes


Theming: build a single AppTheme.dark() returning ThemeData(useMaterial3: true, ...) with a
custom ColorScheme.fromSeed overridden by the exact tokens above, plus a TextTheme from
google_fonts. Expose tokens via a ThemeExtension<AppTokens> so widgets read
Theme.of(context).extension<AppTokens>()!. Never hardcode hex in widgets.
Suggested packages: google_fonts, cached_network_image, shimmer, flutter_animate,
go_router, flutter_riverpod, visibility_detector (rail lazy-load), flutter_staggered_grid_view
(discover grid), palette_generator (optional: tint detail header from poster), intl (dates/countdowns).
Responsiveness: one Responsive helper exposing isCompact/isMedium/isExpanded; build layouts
with LayoutBuilder. Bottom nav on compact; NavigationRail on medium/expanded inside the
NavigationScaffold.
Performance: const everywhere possible; ListView.builder/SliverList for all lists;
cacheExtent tuned on rails; decode images at target size; debounce search; paginate with cursors.
Composition rule: screens are assembled from Section 4 components only. If a screen needs a
visual that isn't a component yet, add it to the component library first, then use it.
Definition of done per screen: all four states implemented (loading/empty/error/data), responsive
at all three breakpoints, reduce-motion respected, semantic labels present, dart analyze clean,
and a widget test covering loading + error + data.



10. Build Order (hand to the agent as the sequence)


Tokens + AppTheme.dark() + ThemeExtension<AppTokens> + typography. Verify on a sample screen.
Core components in this order: PosterCard, ScoreChip, StatusPill, ProgressControl, SectionHeader,
ContentRail, FriendAvatar/AvatarStack, AppButton, AppChip, EmptyState, Skeletons, Toast,
QuickActionSheet, NavigationScaffold.
Redesign existing screens in this order, replacing old UI with the new component system:
Home → Media Detail → My List → Search/Discover → Feed → Discussion → Profile → Watch Party →
Airing Calendar → Notifications → Settings/Group.
Add the Section 8 endpoints as each screen needs them (Home first → endpoint 8.1).
Light theme last (optional). Then full accessibility + reduce-motion pass.


Update PROJECT-STATUS.md as each component and screen is completed, following the existing
phase-tracking convention.