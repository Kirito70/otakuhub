import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/media_detail/models/media_detail.dart';
import 'package:otakuhub/features/media_detail/providers/media_detail_providers.dart';
import 'package:otakuhub/features/media_detail/screens/media_detail_screen.dart';

void main() {
  group('MediaDetailScreen', () {
    const testMediaId = '550e8400-e29b-41d4-a716-446655440000';

    final testMedia = MediaDetail(
      id: testMediaId,
      titleRomaji: 'Shingeki no Kyojin',
      titleEnglish: 'Attack on Titan',
      titleNative: '進撃の巨人',
      mediaType: 'anime',
      format: 'TV',
      status: 'finished',
      synopsis: 'A story about giants and humanity.',
      coverImageLarge: null,
      coverImageMedium: null,
      bannerImage: null,
      averageScore: 8.8,
      popularity: 1,
      episodeCount: 75,
      durationMinutes: 24,
      seasonYear: 2013,
      season: 'spring',
      isAdult: false,
      countryOfOrigin: 'JP',
      genres: [
        GenreInfo(id: 'g1', name: 'Action', slug: 'action'),
        GenreInfo(id: 'g2', name: 'Drama', slug: 'drama'),
      ],
    );

    Widget buildTestApp() {
      return ProviderScope(
        overrides: [
          mediaDetailProvider(testMediaId).overrideWith((ref) async => testMedia),
          episodesProvider(testMediaId).overrideWith((ref) async => [
                EpisodeInfo(id: 'e1', episodeNumber: 1, title: 'To You, in 2000 Years', thumbnailUrl: null),
                EpisodeInfo(id: 'e2', episodeNumber: 2, title: 'That Day', thumbnailUrl: null),
              ]),
          mediaRelationsProvider(testMediaId).overrideWith((ref) async => []),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: MediaDetailScreen(mediaId: testMediaId),
        ),
      );
    }

    testWidgets('renders media title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Attack on Titan'), findsOneWidget);
    });

    testWidgets('renders score', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('8.8'), findsOneWidget);
    });

    testWidgets('renders media type badge', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('ANIME'), findsOneWidget);
    });

    testWidgets('renders episode count', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('75 eps'), findsOneWidget);
    });

    testWidgets('renders tab bar', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Episodes'), findsOneWidget);
      expect(find.text('Info'), findsOneWidget);
      expect(find.text('Related'), findsOneWidget);
    });

    testWidgets('renders episodes in episodes tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Ep. 1'), findsOneWidget);
      expect(find.text('Ep. 2'), findsOneWidget);
    });

    testWidgets('info tab shows synopsis and genres', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Switch to info tab
      await tester.tap(find.text('Info'));
      await tester.pumpAndSettle();

      expect(find.text('Synopsis'), findsOneWidget);
      expect(find.text('Action'), findsOneWidget);
      expect(find.text('Drama'), findsOneWidget);
    });

    testWidgets('shows loading indicator on initial pump', (tester) async {
      // Create a Completer to control when the Future resolves
      final completer = Completer<MediaDetail?>();

      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            mediaDetailProvider(testMediaId).overrideWith((ref) => completer.future),
            episodesProvider(testMediaId).overrideWith((ref) => []),
            mediaRelationsProvider(testMediaId).overrideWith((ref) => []),
          ],
          child: MaterialApp(
            theme: ThemeData.dark(),
            home: MediaDetailScreen(mediaId: testMediaId),
          ),
        ),
      );

      // Should show loading indicator before completer resolves
      expect(find.byType(CircularProgressIndicator), findsOneWidget);

      // Complete the future to avoid pending timer
      completer.complete(null);
      await tester.pumpAndSettle();
    });
  });

  group('MediaDetailScreen error state', () {
    const testMediaId = 'bad-id';

    Widget buildErrorApp() {
      return ProviderScope(
        overrides: [
          mediaDetailProvider(testMediaId).overrideWith((ref) async => null),
          episodesProvider(testMediaId).overrideWith((ref) async => []),
          mediaRelationsProvider(testMediaId).overrideWith((ref) async => []),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: MediaDetailScreen(mediaId: testMediaId),
        ),
      );
    }

    testWidgets('shows not found when media is null', (tester) async {
      await tester.pumpWidget(buildErrorApp());
      await tester.pumpAndSettle();

      expect(find.text('Media not found'), findsOneWidget);
    });
  });
}
