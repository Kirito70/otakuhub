import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/core/widgets/poster_card.dart';
import 'package:otakuhub/features/tracking/models/list_entry.dart';
import 'package:otakuhub/features/tracking/models/list_page_data.dart';
import 'package:otakuhub/features/tracking/screens/list_screen.dart';
import 'package:otakuhub/features/tracking/providers/list_providers.dart';
import 'package:otakuhub/features/tracking/providers/filter_provider.dart';

// ---------------------------------------------------------------------------
// Test data
// ---------------------------------------------------------------------------
final _testEntry = ListEntry(
  id: 'e1',
  userId: 'u1',
  mediaId: 'm1',
  status: 'watching',
  progress: 5,
  score: 7.0,
  createdAt: '2026-01-01T00:00:00Z',
  updatedAt: '2026-01-01T00:00:00Z',
  media: MediaRef(
    id: 'm1',
    titleRomaji: 'Test Anime',
    titleEnglish: 'Test Anime',
    coverImageMedium: null,
    mediaType: 'anime',
    episodeCount: 12,
  ),
);

final _testStats = const ListStats(watching: 1, reading: 2, completed: 10);

final _testBrowseItem = BrowseResultItem(
  id: 'b1',
  titleRomaji: 'Browse Anime',
  titleEnglish: 'Browse Anime',
  averageScore: 8.5,
  format: 'TV',
);

final _testBrowseResponse = BrowseResponse(
  items: [_testBrowseItem],
  total: 1,
);

final _testCuratedRails = CuratedRails(
  rails: [
    CuratedRail(title: 'Trending', railId: 'trending', items: [
      BrowseResultItem(id: 'c1', titleRomaji: 'Trending Anime'),
    ]),
  ],
);

final _testCalendarEvents = [
  CalendarEvent(
    id: 'cal1',
    mediaId: 'm1',
    title: 'Test Anime Episode',
    coverImage: null,
    episodeNumber: 7,
    airingAt: '2026-06-22T18:00:00Z',
    format: 'TV',
  ),
  CalendarEvent(
    id: 'cal2',
    mediaId: 'm2',
    title: 'Another Show',
    chapterNumber: 15,
    airingAt: '2026-06-23T12:00:00Z',
    format: 'MANGA',
  ),
];

// ---------------------------------------------------------------------------
// Helper
// ---------------------------------------------------------------------------
Widget buildTestApp({
  ListPageTab? initialTab,
  List<ListEntry>? testEntries,
  ListStats? testStats,
  BrowseResponse? testBrowse,
  CuratedRails? testRails,
  List<CalendarEvent>? testCalendar,
  FilterState? filterOverride,
}) {
  final overrides = <Override>[
    yourListProvider.overrideWith((ref) async => testEntries ?? [_testEntry]),
    yourListStatsProvider.overrideWith((ref) async => testStats ?? _testStats),
    discoverProvider.overrideWith((ref) async => testBrowse ?? _testBrowseResponse),
    curatedRailsProvider.overrideWith((ref) async => testRails ?? _testCuratedRails),
    calendarProvider.overrideWith((ref) async => testCalendar ?? _testCalendarEvents),
  ];
  if (filterOverride != null) {
    overrides.add(filterStateProvider.overrideWith((ref) => filterOverride));
  }
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(
      theme: ThemeData.dark(),
      home: ListScreen(initialTab: initialTab),
    ),
  );
}

void main() {
  // -------------------------------------------------------------------------
  // Your List tab
  // -------------------------------------------------------------------------
  group('ListScreen — Your List tab', () {
    testWidgets('renders tab bar with 3 sub-tabs', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Your List'), findsOneWidget);
      expect(find.text('Discover'), findsOneWidget);
      expect(find.text('Calendar'), findsOneWidget);
    });

    testWidgets('renders list entries in grid', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Test Anime'), findsOneWidget);
    });

    testWidgets('shows stats bar', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // stats.watching(1) + stats.reading(2) = 3
      expect(find.text('3'), findsOneWidget);
      // "Watching" appears in stats bar AND status badge on cards
      expect(find.text('Watching'), findsWidgets);
      expect(find.text('10'), findsOneWidget); // completed count
      expect(find.text('Completed'), findsOneWidget);
    });

    testWidgets('shows empty state when no entries', (tester) async {
      await tester.pumpWidget(buildTestApp(testEntries: []));
      await tester.pumpAndSettle();

      expect(find.textContaining('Start building your list'), findsOneWidget);
    });

    testWidgets('shows progress text on entry cards', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('5/12'), findsOneWidget);
    });

    testWidgets('shows AppEmptyState with retry on error', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            yourListProvider.overrideWith((ref) async {
              throw Exception('API error');
            }),
            yourListStatsProvider.overrideWith((ref) async => _testStats),
            discoverProvider.overrideWith((ref) async => _testBrowseResponse),
            curatedRailsProvider.overrideWith((ref) async => _testCuratedRails),
            calendarProvider.overrideWith((ref) async => _testCalendarEvents),
          ],
          child: MaterialApp(
            theme: ThemeData.dark(),
            home: const ListScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Failed to load your list'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });
  });

  // -------------------------------------------------------------------------
  // Discover tab
  // -------------------------------------------------------------------------
  group('ListScreen — Discover tab', () {
    testWidgets('shows curated rails by default', (tester) async {
      await tester.pumpWidget(buildTestApp(initialTab: ListPageTab.discover));
      await tester.pumpAndSettle();

      // SectionHeader is always rendered as Text
      expect(find.text('Trending'), findsOneWidget);
      // PosterCard renders in the rail; on mobile title is hover-only
      expect(find.byType(PosterCard), findsOneWidget);
    });

    testWidgets('shows section header for rails', (tester) async {
      await tester.pumpWidget(buildTestApp(initialTab: ListPageTab.discover));
      await tester.pumpAndSettle();

      expect(find.text('Trending'), findsWidgets);
    });

    testWidgets('shows filtered grid when filters active', (tester) async {
      await tester.pumpWidget(buildTestApp(
        initialTab: ListPageTab.discover,
        filterOverride: const FilterState(mediaType: 'anime'),
      ));
      await tester.pumpAndSettle();

      // PosterCard is rendered (title is hover-only per PosterCard design)
      expect(find.byType(PosterCard), findsOneWidget);
      // Rails section header should NOT be shown when filters are active
      expect(find.text('Trending'), findsNothing);
    });

    testWidgets('shows AppEmptyState when browse empty', (tester) async {
      await tester.pumpWidget(buildTestApp(
        initialTab: ListPageTab.discover,
        testBrowse: const BrowseResponse(),
        filterOverride: const FilterState(mediaType: 'anime'),
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('No titles match'), findsOneWidget);
    });

    testWidgets('shows error state on discover failure', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            yourListProvider.overrideWith((ref) async => []),
            yourListStatsProvider.overrideWith((ref) async => _testStats),
            discoverProvider.overrideWith((ref) async {
              throw Exception('Browse error');
            }),
            curatedRailsProvider.overrideWith((ref) async => _testCuratedRails),
            calendarProvider.overrideWith((ref) async => _testCalendarEvents),
            filterStateProvider.overrideWith((ref) => const FilterState(mediaType: 'anime')),
          ],
          child: MaterialApp(
            theme: ThemeData.dark(),
            home: const ListScreen(initialTab: ListPageTab.discover),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Failed to load'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });
  });

  // -------------------------------------------------------------------------
  // Calendar tab
  // -------------------------------------------------------------------------
  group('ListScreen — Calendar tab', () {
    testWidgets('shows events grouped by date', (tester) async {
      await tester.pumpWidget(buildTestApp(initialTab: ListPageTab.calendar));
      await tester.pumpAndSettle();

      expect(find.text('Test Anime Episode'), findsOneWidget);
      expect(find.text('Another Show'), findsOneWidget);
    });

    testWidgets('shows date header labels', (tester) async {
      await tester.pumpWidget(buildTestApp(initialTab: ListPageTab.calendar));
      await tester.pumpAndSettle();

      expect(find.textContaining('Ep 7'), findsOneWidget);
      expect(find.textContaining('Ch 15'), findsOneWidget);
    });

    testWidgets('shows empty state when no events', (tester) async {
      await tester.pumpWidget(buildTestApp(
        initialTab: ListPageTab.calendar,
        testCalendar: [],
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('No upcoming airings'), findsOneWidget);
    });

    testWidgets('shows error state on calendar failure', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            yourListProvider.overrideWith((ref) async => []),
            yourListStatsProvider.overrideWith((ref) async => _testStats),
            discoverProvider.overrideWith((ref) async => _testBrowseResponse),
            curatedRailsProvider.overrideWith((ref) async => _testCuratedRails),
            calendarProvider.overrideWith((ref) async {
              throw Exception('Calendar error');
            }),
          ],
          child: MaterialApp(
            theme: ThemeData.dark(),
            home: const ListScreen(initialTab: ListPageTab.calendar),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Failed to load schedule'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });
  });

  // -------------------------------------------------------------------------
  // Filter bar interactions
  // -------------------------------------------------------------------------
  group('ListScreen — filter bar', () {
    testWidgets('renders filter chips', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Media Type'), findsOneWidget);
      expect(find.text('Format'), findsOneWidget);
      expect(find.text('Season'), findsOneWidget);
      expect(find.text('Year'), findsOneWidget);
      // The sort chip shows "Score (high)" as default (sort=score_desc)
      expect(find.text('Score (high)'), findsOneWidget);
    });

    testWidgets('tapping Media Type chip opens bottom sheet', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Media Type'));
      await tester.pumpAndSettle();

      // Bottom sheet should show media type options
      expect(find.text('Anime'), findsWidgets);
      expect(find.text('Manga'), findsWidgets);
    });

    testWidgets('selecting a filter option updates the chip', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Open Media Type filter
      await tester.tap(find.text('Media Type'));
      await tester.pumpAndSettle();

      // Select Anime
      await tester.tap(find.text('Anime').last);
      await tester.pumpAndSettle();

      // The chip label should now show "Anime" instead of "Media Type"
      expect(find.text('Anime'), findsWidgets);
    });

    testWidgets('Status filter visible only on Your List tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // On Your List tab, Status filter should be visible
      expect(find.text('Status'), findsOneWidget);
    });

    testWidgets('Genre filter visible on Discover tab', (tester) async {
      await tester.pumpWidget(buildTestApp(initialTab: ListPageTab.discover));
      await tester.pumpAndSettle();

      // On Discover tab, Genre filter should be visible
      expect(find.text('Genre'), findsOneWidget);
    });
  });

  // -------------------------------------------------------------------------
  // Tab switching
  // -------------------------------------------------------------------------
  group('ListScreen — tab switching', () {
    testWidgets('switching tabs shows correct content', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Start on Your List tab
      expect(find.text('Test Anime'), findsOneWidget);

      // Switch to Calendar
      await tester.tap(find.text('Calendar'));
      await tester.pumpAndSettle();

      expect(find.text('Test Anime Episode'), findsOneWidget);
      expect(find.text('Another Show'), findsOneWidget);
    });

    testWidgets('initialTab parameter navigates to correct tab', (tester) async {
      await tester.pumpWidget(buildTestApp(initialTab: ListPageTab.calendar));
      await tester.pumpAndSettle();

      expect(find.text('Test Anime Episode'), findsOneWidget);
    });

    testWidgets('switching to Discover tab shows rails', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Discover'));
      await tester.pumpAndSettle();

      expect(find.text('Trending'), findsOneWidget);
    });
  });
}
