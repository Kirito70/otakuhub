import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/social/screens/discussion_list_screen.dart';

void main() {
  group('DiscussionListScreen', () {
    Widget buildTestApp() {
      return ProviderScope(
        // No provider overrides needed — threads tab does not invoke
        // discussionListNotifierProvider until a media ID is searched.
        // createDiscussionActionProvider.build() returns void immediately.
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const DiscussionListScreen(),
        ),
      );
    }

    testWidgets('renders title and tabs', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Discussions'), findsOneWidget);
      expect(find.text('Threads'), findsOneWidget);
      expect(find.text('Create'), findsOneWidget);
    });

    testWidgets('shows media id input on threads tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Media ID'), findsOneWidget);
      expect(find.byIcon(Icons.search), findsOneWidget);
    });

    testWidgets('create tab has form fields', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      await tester.tap(find.text('Create'));
      await tester.pump(const Duration(milliseconds: 300));
      await tester.pump(const Duration(milliseconds: 100));

      expect(find.text('Body *'), findsOneWidget);
      expect(find.text('Contains spoilers'), findsOneWidget);
      expect(find.text('Create Discussion'), findsOneWidget);
    });

    testWidgets('shows hint text on threads tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(
        find.textContaining('Enter a Media ID above'),
        findsOneWidget,
      );
    });
  });
}
