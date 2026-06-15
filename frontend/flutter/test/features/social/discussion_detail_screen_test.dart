import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/social/models/discussion.dart';
import 'package:otakuhub/features/social/providers/discussions_provider.dart';
import 'package:otakuhub/features/social/screens/discussion_detail_screen.dart';

class _MockReplyListNotifier extends ReplyListNotifier {
  @override
  Future<ReplyListResponse> build(String discussionId) async =>
      const ReplyListResponse();
}

void main() {
  group('DiscussionDetailScreen', () {
    const testDiscussionId = 'd1';

    Widget buildTestApp() {
      return ProviderScope(
        overrides: [
          replyListNotifierProvider(testDiscussionId).overrideWith(
            () => _MockReplyListNotifier(),
          ),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const DiscussionDetailScreen(
            discussionId: testDiscussionId,
          ),
        ),
      );
    }

    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Discussion'), findsOneWidget);
    });

    testWidgets('shows empty state when no replies', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(
        find.textContaining('No replies yet'),
        findsOneWidget,
      );
    });

    testWidgets('shows reply input bar', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Spoiler'), findsOneWidget);
      expect(find.byIcon(Icons.send), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget);
    });
  });
}
