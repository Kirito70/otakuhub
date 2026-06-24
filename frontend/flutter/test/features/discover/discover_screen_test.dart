import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/discover/models/home_data.dart';
import 'package:otakuhub/features/discover/providers/home_provider.dart';
import 'package:otakuhub/features/discover/screens/home_screen.dart';

void main() {
  group('HomeScreen', () {
    final testSpotlight = HomeSpotlightItem(
      id: 's1',
      titleRomaji: 'Spotlight Anime',
      format: 'TV',
      averageScore: 8.5,
      seasonYear: 2026,
      synopsis: 'A great anime',
    );

    final testGenreItem = GenreRailItem(
      id: 'g1',
      titleRomaji: 'Action Anime',
    );

    final testGenreRail = GenreRail(
      genreId: 'action',
      genreName: 'Action',
      items: [testGenreItem],
    );

    final testSection = MediaTypeSection(
      mediaType: 'anime',
      mediaTypeLabel: 'Anime',
      genreRails: [testGenreRail],
    );

    final testHomeData = HomeData(
      spotlight: [testSpotlight],
      mediaTypeSections: [testSection],
    );

    Widget buildTestApp(HomeData homeData) {
      return ProviderScope(
        overrides: [
          homeProvider.overrideWith((ref) async => homeData),
        ],
        child: const MaterialApp(
          home: HomeScreen(),
        ),
      );
    }

    testWidgets('renders spotlight hero when data available', (tester) async {
      tester.view.physicalSize = const Size(1200, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());
      await tester.pumpWidget(buildTestApp(testHomeData));
      await tester.pumpAndSettle();

      expect(find.text('Spotlight Anime'), findsOneWidget);
      expect(find.text('A great anime'), findsOneWidget);
    });

    testWidgets('renders media type sections with genre rails', (tester) async {
      tester.view.physicalSize = const Size(1200, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());
      await tester.pumpWidget(buildTestApp(testHomeData));
      await tester.pumpAndSettle();

      expect(find.text('Anime'), findsOneWidget);
      expect(find.text('Action'), findsOneWidget);
    });

    testWidgets('renders "Add to list" and "Details" buttons', (tester) async {
      tester.view.physicalSize = const Size(1200, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());
      await tester.pumpWidget(buildTestApp(testHomeData));
      await tester.pumpAndSettle();

      expect(find.text('+ Add to list'), findsOneWidget);
      expect(find.text('Details'), findsOneWidget);
    });

    testWidgets('shows score chip on spotlight', (tester) async {
      tester.view.physicalSize = const Size(1200, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(() => tester.view.resetPhysicalSize());
      await tester.pumpWidget(buildTestApp(testHomeData));
      await tester.pumpAndSettle();

      expect(find.text('★ 8.5'), findsOneWidget);
    });
  });

  group('HomeScreen empty/error states', () {
    Widget buildEmptyApp() {
      return ProviderScope(
        overrides: [
          homeProvider.overrideWith((ref) async => const HomeData()),
        ],
        child: const MaterialApp(
          home: HomeScreen(),
        ),
      );
    }

    testWidgets('shows empty state when no data', (tester) async {
      await tester.pumpWidget(buildEmptyApp());
      await tester.pumpAndSettle();

      expect(
        find.textContaining('No media data yet'),
        findsOneWidget,
      );
    });

    testWidgets('shows error state on API failure', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            homeProvider.overrideWith((ref) async {
              throw Exception('API error');
            }),
          ],
          child: const MaterialApp(
            home: HomeScreen(),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(
        find.textContaining('Could not load your home feed'),
        findsOneWidget,
      );
    });
  });
}
