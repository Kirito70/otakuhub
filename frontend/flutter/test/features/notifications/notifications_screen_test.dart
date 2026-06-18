import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/notifications/models/notification_models.dart';
import 'package:otakuhub/features/notifications/providers/notification_providers.dart';
import 'package:otakuhub/features/notifications/screens/notifications_screen.dart';

// --- Mock notifiers ---

class _MockAllNotifier extends AllNotificationsNotifier {
  @override
  Future<NotificationListResponse> build() async => NotificationListResponse(
        items: const [],
        total: 0,
        limit: 50,
        offset: 0,
      );
}

class _MockUnreadNotifier extends UnreadNotificationsNotifier {
  @override
  Future<NotificationListResponse> build() async => NotificationListResponse(
        items: const [],
        total: 0,
        limit: 50,
        offset: 0,
      );
}

class _MockMarkReadNotifier extends MarkReadNotifier {
  @override
  Future<NotificationMarkReadResponse?> build() async => null;
}

class _MockDeleteNotifier extends DeleteNotificationNotifier {
  @override
  Future<bool?> build() async => null;
}

class _MockLoadingAll extends AllNotificationsNotifier {
  @override
  Future<NotificationListResponse> build() async {
    return Completer<NotificationListResponse>().future;
  }
}

class _MockAllWithItems extends AllNotificationsNotifier {
  @override
  Future<NotificationListResponse> build() async => NotificationListResponse(
        items: [_mockNotification, _mockReadNotification],
        total: 2,
        limit: 50,
        offset: 0,
      );
}

// --- Shared mock data ---

final _mockNotification = NotificationItem(
  id: 'notif-1',
  userId: 'user-1',
  type: 'new_episode',
  title: 'New Episode of Solo Leveling',
  body: 'Episode 13 is now available',
  isRead: false,
  createdAt: DateTime.now(),
);

final _mockReadNotification = NotificationItem(
  id: 'notif-2',
  userId: 'user-1',
  type: 'recommendation',
  title: 'Friend recommended you One Piece',
  body: 'You should check it out!',
  isRead: true,
  createdAt: DateTime.now().subtract(const Duration(hours: 2)),
);

Widget buildTestApp() {
  return ProviderScope(
    overrides: [
      allNotificationsNotifierProvider
          .overrideWith(() => _MockAllNotifier()),
      unreadNotificationsNotifierProvider
          .overrideWith(() => _MockUnreadNotifier()),
      markReadNotifierProvider.overrideWith(() => _MockMarkReadNotifier()),
      deleteNotificationNotifierProvider
          .overrideWith(() => _MockDeleteNotifier()),
    ],
    child: MaterialApp(
      theme: ThemeData.dark(),
      home: const NotificationsScreen(),
    ),
  );
}

void main() {
  group('NotificationsScreen', () {
    testWidgets('renders app bar title and mark-all-read button',
        (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Notifications'), findsOneWidget);
      expect(find.byIcon(Icons.done_all_outlined), findsOneWidget);
    });

    testWidgets('renders All and Unread tabs', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('All'), findsOneWidget);
      expect(find.text('Unread'), findsOneWidget);
      expect(find.byType(TabBar), findsOneWidget);
      expect(find.byType(TabBarView), findsOneWidget);
    });

    testWidgets('shows loading indicator initially on All tab',
        (tester) async {
      final container = ProviderScope(
        overrides: [
          allNotificationsNotifierProvider
              .overrideWith(() => _MockLoadingAll()),
          unreadNotificationsNotifierProvider
              .overrideWith(() => _MockUnreadNotifier()),
          markReadNotifierProvider.overrideWith(() => _MockMarkReadNotifier()),
          deleteNotificationNotifierProvider
              .overrideWith(() => _MockDeleteNotifier()),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const NotificationsScreen(),
        ),
      );

      await tester.pumpWidget(container);
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows empty state when no notifications', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('No notifications yet'), findsOneWidget);
      expect(
        find.text("We'll let you know when something happens"),
        findsOneWidget,
      );
    });

    testWidgets('All tab shows notification items', (tester) async {
      final container = ProviderScope(
        overrides: [
          allNotificationsNotifierProvider
              .overrideWith(() => _MockAllWithItems()),
          unreadNotificationsNotifierProvider
              .overrideWith(() => _MockUnreadNotifier()),
          markReadNotifierProvider.overrideWith(() => _MockMarkReadNotifier()),
          deleteNotificationNotifierProvider
              .overrideWith(() => _MockDeleteNotifier()),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const NotificationsScreen(),
        ),
      );

      await tester.pumpWidget(container);
      await tester.pump();

      expect(
        find.text('New Episode of Solo Leveling'),
        findsOneWidget,
      );
      expect(find.text('Episode 13 is now available'), findsOneWidget);
      expect(find.text('Friend recommended you One Piece'), findsOneWidget);
    });

    testWidgets('switching to Unread tab shows empty state',
        (tester) async {
      final container = ProviderScope(
        overrides: [
          allNotificationsNotifierProvider
              .overrideWith(() => _MockAllNotifier()),
          unreadNotificationsNotifierProvider
              .overrideWith(() => _MockUnreadNotifier()),
          markReadNotifierProvider.overrideWith(() => _MockMarkReadNotifier()),
          deleteNotificationNotifierProvider
              .overrideWith(() => _MockDeleteNotifier()),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const NotificationsScreen(initialTabIndex: 1),
        ),
      );

      await tester.pumpWidget(container);
      await tester.pump();

      expect(find.text('All caught up!'), findsOneWidget);
      expect(find.text('No unread notifications'), findsOneWidget);
    });

    testWidgets('error state shows retry button', (tester) async {
      final container = ProviderScope(
        overrides: [
          allNotificationsNotifierProvider.overrideWith(
            () => _MockAllNotifier()
              ..state = AsyncError(
                Exception('Failed'),
                StackTrace.current,
              ),
          ),
          unreadNotificationsNotifierProvider
              .overrideWith(() => _MockUnreadNotifier()),
          markReadNotifierProvider.overrideWith(() => _MockMarkReadNotifier()),
          deleteNotificationNotifierProvider
              .overrideWith(() => _MockDeleteNotifier()),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const NotificationsScreen(),
        ),
      );

      await tester.pumpWidget(container);
      await tester.pump();

      expect(find.text('Failed to load notifications'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });
  });
}
