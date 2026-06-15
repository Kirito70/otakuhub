import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/tracking/screens/import_list_screen.dart';

void main() {
  group('ImportListScreen', () {
    Widget buildTestApp() {
      return ProviderScope(
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const ImportListScreen(),
        ),
      );
    }

    testWidgets('renders title and tabs', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Import List'), findsOneWidget);
      expect(find.text('AniList'), findsOneWidget);
      expect(find.text('MyAnimeList'), findsOneWidget);
    });

    testWidgets('renders username field', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Username (optional)'), findsOneWidget);
    });

    testWidgets('renders start import button', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Start Import'), findsOneWidget);
    });

    testWidgets('renders overwrite existing toggle', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Overwrite existing entries'), findsOneWidget);
    });

    testWidgets('shows AniList info banner by default', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(
        find.textContaining('3–20 characters'),
        findsOneWidget,
      );
    });

    testWidgets('switching tabs shows MAL info', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Tap MyAnimeList tab
      await tester.tap(find.text('MyAnimeList'));
      await tester.pumpAndSettle();

      expect(
        find.textContaining('3–16 characters'),
        findsOneWidget,
      );
    });

    testWidgets('validates AniList username format', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Enter invalid AniList username (contains a space)
      await tester.enterText(find.byType(TextFormField), 'invalid user!');
      await tester.tap(find.text('Start Import'));
      await tester.pumpAndSettle();

      // The validation error (red text) should show — not the info banner
      // Use a more specific match that only matches the error message
      expect(
        find.textContaining('only'),
        findsOneWidget,
      );
    });

    testWidgets('validates MAL username format on tab switch', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Switch to MAL tab
      await tester.tap(find.text('MyAnimeList'));
      await tester.pumpAndSettle();

      // Enter invalid MAL username (contains a dash)
      await tester.enterText(find.byType(TextFormField), 'invalid-name');
      await tester.tap(find.text('Start Import'));
      await tester.pumpAndSettle();

      // The validation error (red text) should show — not the info banner
      expect(
        find.textContaining('only'),
        findsOneWidget,
      );
    });

    testWidgets('MAL tab shows correct rules', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Switch to MAL tab
      await tester.tap(find.text('MyAnimeList'));
      await tester.pumpAndSettle();

      expect(
        find.textContaining('MyAnimeList usernames'),
        findsOneWidget,
      );
    });
  });
}
