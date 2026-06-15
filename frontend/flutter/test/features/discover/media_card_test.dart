import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/discover/models/media_item.dart';
import 'package:otakuhub/features/discover/widgets/media_card.dart';

void main() {
  group('MediaCard', () {
    final testItem = MediaItem(
      id: '550e8400-e29b-41d4-a716-446655440000',
      titleRomaji: 'Test Anime',
      titleEnglish: 'Test Anime English',
      mediaType: 'anime',
      format: 'TV',
      status: 'releasing',
      coverImageMedium: null,
      averageScore: 8.5,
      episodeCount: 24,
      seasonYear: 2026,
      season: 'spring',
    );

    testWidgets('renders title and score', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: MediaCard(item: testItem),
          ),
        ),
      );

      expect(find.text('Test Anime English'), findsOneWidget);
      expect(find.text('8.5'), findsOneWidget);
    });

    testWidgets('renders media type badge', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: MediaCard(item: testItem),
          ),
        ),
      );

      expect(find.text('ANIME'), findsOneWidget);
    });

    testWidgets('renders progress bar when progressPercent provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: MediaCard(item: testItem, progressPercent: 0.5),
          ),
        ),
      );

      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });

    testWidgets('shows placeholder when no cover image', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: MediaCard(item: testItem),
          ),
        ),
      );

      // The placeholder icon should be visible since coverImageMedium is null
      expect(find.byIcon(Icons.movie_outlined), findsOneWidget);
    });

    testWidgets('renders without English title fallback', (tester) async {
      final jpItem = MediaItem(
        id: '660e8400-e29b-41d4-a716-446655440001',
        titleRomaji: 'Japanese Title',
        titleEnglish: null,
        mediaType: 'manga',
        status: 'finished',
      );

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: MediaCard(item: jpItem),
          ),
        ),
      );

      expect(find.text('Japanese Title'), findsOneWidget);
    });
  });
}
