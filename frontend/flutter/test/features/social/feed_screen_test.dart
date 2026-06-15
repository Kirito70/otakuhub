import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/social/models/feed_item.dart';
import 'package:otakuhub/features/social/providers/feed_provider.dart';
import 'package:otakuhub/features/social/screens/feed_screen.dart';

class _MockGroupFeedNotifier extends GroupFeedNotifier {
  @override
  Future<FeedResponse> build() async => const FeedResponse();
}

class _MockMyActivityNotifier extends MyActivityNotifier {
  @override
  Future<FeedResponse> build() async => const FeedResponse();
}

void main() {
  group('FeedScreen', () {
    Widget buildTestApp() {
      return ProviderScope(
        overrides: [
          groupFeedNotifierProvider.overrideWith(
            () => _MockGroupFeedNotifier(),
          ),
          myActivityNotifierProvider.overrideWith(
            () => _MockMyActivityNotifier(),
          ),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const FeedScreen(),
        ),
      );
    }

    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Activity Feed'), findsOneWidget);
    });

    testWidgets('renders tab bar and tab bar view', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Group Activity'), findsOneWidget);
      expect(find.text('My Activity'), findsOneWidget);
      expect(find.byType(TabBar), findsOneWidget);
      expect(find.byType(TabBarView), findsOneWidget);
    });

    testWidgets('shows empty state when no activity', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(
        find.textContaining('No group activity yet'),
        findsOneWidget,
      );
    });
  });
}
