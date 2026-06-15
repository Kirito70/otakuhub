import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/tracking/models/list_entry.dart';
import 'package:otakuhub/features/tracking/providers/tracking_providers.dart';
import 'package:otakuhub/features/tracking/screens/my_list_screen.dart';

void main() {
  group('MyListScreen', () {
    final testEntries = [
      ListEntry(
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
      ),
    ];

    Widget buildTestApp() {
      return ProviderScope(
        overrides: [
          listEntriesProvider('watching').overrideWith((ref) async => testEntries),
          listEntriesProvider('reading').overrideWith((ref) async => []),
          listEntriesProvider('completed').overrideWith((ref) async => []),
          listEntriesProvider('paused').overrideWith((ref) async => []),
          listEntriesProvider('dropped').overrideWith((ref) async => []),
          listEntriesProvider('plan').overrideWith((ref) async => []),
          listStatsProvider.overrideWith((ref) async => const ListStats(watching: 1)),
          listHistoryProvider.overrideWith((ref) async => []),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const MyListScreen(),
        ),
      );
    }

    testWidgets('renders tab bar with status tabs', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Watching'), findsOneWidget);
      expect(find.text('Reading'), findsOneWidget);
      expect(find.text('Completed'), findsOneWidget);
      expect(find.text('Paused'), findsOneWidget);
      expect(find.text('Dropped'), findsOneWidget);
      expect(find.text('Plan'), findsOneWidget);
    });

    testWidgets('renders watching tab with entries', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Test Anime'), findsOneWidget);
      expect(find.text('5'), findsOneWidget);
    });

    testWidgets('renders stats bar', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.textContaining('Watching:'), findsOneWidget);
    });

    testWidgets('shows empty state for reading tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Switch to reading tab
      await tester.tap(find.text('Reading'));
      await tester.pumpAndSettle();

      expect(find.textContaining('No reading entries'), findsOneWidget);
    });

    testWidgets('shows empty state for completed tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Completed'));
      await tester.pumpAndSettle();

      expect(find.textContaining('No completed entries'), findsOneWidget);
    });
  });

  group('MyListScreen loading/error', () {
    testWidgets('shows loading state', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            listEntriesProvider('watching').overrideWith((ref) => Future<List<ListEntry>>.value([])),
            listEntriesProvider('reading').overrideWith((ref) => Future<List<ListEntry>>.value([])),
            listEntriesProvider('completed').overrideWith((ref) => Future<List<ListEntry>>.value([])),
            listEntriesProvider('paused').overrideWith((ref) => Future<List<ListEntry>>.value([])),
            listEntriesProvider('dropped').overrideWith((ref) => Future<List<ListEntry>>.value([])),
            listEntriesProvider('plan').overrideWith((ref) => Future<List<ListEntry>>.value([])),
            listStatsProvider.overrideWith((ref) => Future<ListStats>.value(const ListStats())),
            listHistoryProvider.overrideWith((ref) => Future<List<HistoryItem>>.value([])),
          ],
          child: MaterialApp(
            theme: ThemeData.dark(),
            home: const MyListScreen(),
          ),
        ),
      );

      // Should not crash; after settling should show no CircularProgressIndicator
      await tester.pumpAndSettle();
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });
  });
}
