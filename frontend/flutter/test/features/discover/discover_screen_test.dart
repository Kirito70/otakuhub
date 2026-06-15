import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/discover/models/media_item.dart';
import 'package:otakuhub/features/discover/providers/discover_providers.dart';
import 'package:otakuhub/features/discover/screens/discover_screen.dart';

void main() {
  group('DiscoverScreen', () {
    final testItems = [
      MediaItem(
        id: '1',
        titleRomaji: 'Anime 1',
        mediaType: 'anime',
        format: 'TV',
        status: 'releasing',
        averageScore: 8.5,
        episodeCount: 12,
      ),
      MediaItem(
        id: '2',
        titleRomaji: 'Anime 2',
        mediaType: 'anime',
        format: 'TV',
        status: 'finished',
        averageScore: 7.0,
        episodeCount: 24,
      ),
    ];

    Widget buildTestApp() {
      return ProviderScope(
        overrides: [
          // Override trending provider with test data
          trendingProvider.overrideWith((ref) async => testItems),
          // Override seasonal provider with test data
          seasonalProvider.overrideWith((ref) async => testItems),
          // Override search to return empty
          searchResultsProvider.overrideWith((ref) async => []),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const DiscoverScreen(),
        ),
      );
    }

    testWidgets('renders tab bar with three tabs', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Search'), findsOneWidget);
      expect(find.text('Trending'), findsOneWidget);
      expect(find.text('New Releases'), findsOneWidget);
    });

    testWidgets('renders trending tab with data', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Switch to trending tab
      await tester.tap(find.text('Trending'));
      await tester.pumpAndSettle();

      expect(find.text('Anime 1'), findsOneWidget);
      expect(find.text('Anime 2'), findsOneWidget);
    });

    testWidgets('renders seasonal tab with data', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Switch to seasonal tab
      await tester.tap(find.text('New Releases'));
      await tester.pumpAndSettle();

      expect(find.text('Anime 1'), findsOneWidget);
      expect(find.text('Anime 2'), findsOneWidget);
    });

    testWidgets('shows search field on search tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Search tab should have a text field
      expect(find.byType(TextField), findsOneWidget);
    });

    testWidgets('search tab shows empty state', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.textContaining('Enter a search term'), findsOneWidget);
    });
  });

  group('DiscoverScreen empty/error states', () {
    Widget buildEmptyApp() {
      return ProviderScope(
        overrides: [
          trendingProvider.overrideWith((ref) async => []),
          seasonalProvider.overrideWith((ref) async => []),
          searchResultsProvider.overrideWith((ref) async => []),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const DiscoverScreen(),
        ),
      );
    }

    testWidgets('trending tab shows empty state', (tester) async {
      await tester.pumpWidget(buildEmptyApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('Trending'));
      await tester.pumpAndSettle();

      expect(find.text('No trending data'), findsOneWidget);
    });

    testWidgets('new releases tab shows empty state', (tester) async {
      await tester.pumpWidget(buildEmptyApp());
      await tester.pumpAndSettle();

      await tester.tap(find.text('New Releases'));
      await tester.pumpAndSettle();

      expect(find.text('No seasonal releases'), findsOneWidget);
    });
  });
}
