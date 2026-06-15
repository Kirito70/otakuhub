import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/social/models/recommendation.dart';
import 'package:otakuhub/features/social/providers/recommendations_provider.dart';
import 'package:otakuhub/features/social/screens/recommendations_screen.dart';

class _MockInboxNotifier extends InboxNotifier {
  @override
  Future<RecommendationListResponse> build() async =>
      const RecommendationListResponse();
}

class _MockSentNotifier extends SentNotifier {
  @override
  Future<RecommendationListResponse> build() async =>
      const RecommendationListResponse();
}

void main() {
  group('RecommendationsScreen', () {
    Widget buildTestApp() {
      return ProviderScope(
        overrides: [
          inboxNotifierProvider.overrideWith(() => _MockInboxNotifier()),
          sentNotifierProvider.overrideWith(() => _MockSentNotifier()),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const RecommendationsScreen(),
        ),
      );
    }

    testWidgets('renders title and tabs without hanging', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Recommendations'), findsOneWidget);
      expect(find.text('Inbox'), findsOneWidget);
      expect(find.text('Sent'), findsOneWidget);
    });

    testWidgets('renders scaffolds and tab bar', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.byType(TabBar), findsOneWidget);
      expect(find.byType(TabBarView), findsOneWidget);
    });

    testWidgets('shows empty state on inbox tab', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(
        find.textContaining('No recommendations in your inbox'),
        findsOneWidget,
      );
    });
  });
}
