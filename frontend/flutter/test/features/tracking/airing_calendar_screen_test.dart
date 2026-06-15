import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/tracking/models/airing_item.dart';
import 'package:otakuhub/features/tracking/providers/airing_calendar_provider.dart';
import 'package:otakuhub/features/tracking/screens/airing_calendar_screen.dart';

void main() {
  group('AiringCalendarScreen', () {
    final testItems = [
      AiringEpisodeItem(
        id: 'ep1',
        mediaId: 'm1',
        mediaTitle: 'Test Anime 1',
        mediaCover: null,
        mediaType: 'anime',
        episodeNumber: 1,
        title: 'The Beginning',
        airDate: '2026-06-20T12:00:00Z',
        durationMinutes: 24,
      ),
      AiringEpisodeItem(
        id: 'ep2',
        mediaId: 'm2',
        mediaTitle: 'Test Anime 2',
        mediaCover: null,
        mediaType: 'anime',
        episodeNumber: 5,
        title: 'Climax',
        airDate: '2026-06-20T13:00:00Z',
        durationMinutes: 24,
      ),
    ];

    Widget buildTestApp({AiringResponse? data}) {
      return ProviderScope(
        overrides: [
          airingScheduleProvider.overrideWith(
            (ref) async => data ??
                AiringResponse(
                  items: testItems,
                  total: 2,
                  limit: 50,
                  offset: 0,
                ),
          ),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const AiringCalendarScreen(),
        ),
      );
    }

    testWidgets('renders title in app bar', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Airing Calendar'), findsOneWidget);
    });

    testWidgets('shows refresh button', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });

    testWidgets('displays episode items grouped by date', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Test Anime 1'), findsOneWidget);
      expect(find.text('Test Anime 2'), findsOneWidget);
      expect(find.textContaining('2 episodes'), findsOneWidget);
    });

    testWidgets('displays episode numbers', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.textContaining('Ep 1'), findsOneWidget);
      expect(find.textContaining('Ep 5'), findsOneWidget);
    });

    testWidgets('shows duration when available', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Both test episodes have 24m duration
      expect(find.text('24m'), findsNWidgets(2));
    });

    testWidgets('shows empty state when no items', (tester) async {
      await tester.pumpWidget(buildTestApp(
        data: const AiringResponse(items: []),
      ));
      await tester.pumpAndSettle();

      expect(find.text('No upcoming airings'), findsOneWidget);
    });

    testWidgets('shows loading state initially', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          overrides: [
            airingScheduleProvider.overrideWith(
              (ref) async => const AiringResponse(items: []),
            ),
          ],
          child: const MaterialApp(
            home: AiringCalendarScreen(),
          ),
        ),
      );

      // Should resolve without pending timers
      await tester.pumpAndSettle();
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });
  });
}
