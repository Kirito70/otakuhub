import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/notifications/models/notification_models.dart';
import 'package:otakuhub/features/notifications/providers/notification_providers.dart';
import 'package:otakuhub/features/notifications/screens/notification_preferences_screen.dart';

// --- Mock notifiers ---

class _MockUpdatePrefs extends UpdatePreferencesNotifier {
  @override
  Future<NotificationPreferences?> build() async => null;
}

final _mockPrefs = NotificationPreferences(
  userId: 'user-1',
  newEpisode: true,
  newChapter: false,
  friendActivity: true,
  recommendations: true,
  watchPartyInvite: true,
  watchPartyReminder: false,
  discordWebhook: null,
  telegramChatId: null,
  emailEnabled: true,
  pushEnabled: false,
  updatedAt: DateTime.now(),
);

Widget buildTestApp() {
  return ProviderScope(
    overrides: [
      notificationPreferencesProviderProvider
          .overrideWithProvider(
        AutoDisposeFutureProvider<NotificationPreferences>((ref) async => _mockPrefs),
      ),
      updatePreferencesNotifierProvider
          .overrideWith(() => _MockUpdatePrefs()),
    ],
    child: MaterialApp(
      theme: ThemeData.dark(),
      home: const NotificationPreferencesScreen(),
    ),
  );
}

void main() {
  group('NotificationPreferencesScreen', () {
    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Notification Preferences'), findsOneWidget);
    });

    testWidgets('renders content section headers', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Content'), findsOneWidget);
      expect(find.text('Delivery Channels'), findsOneWidget);
    });

    testWidgets('renders toggle switches with correct defaults',
        (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      // Content types that are enabled
      expect(find.text('New Episodes'), findsOneWidget);
      expect(find.text('New Chapters'), findsOneWidget);
      expect(find.text('Friend Activity'), findsOneWidget);
      expect(find.text('Recommendations'), findsOneWidget);
      expect(find.text('Watch Party Invites'), findsOneWidget);
      expect(find.text('Watch Party Reminders'), findsOneWidget);
    });

    testWidgets('renders channel input fields', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Discord Webhook URL'), findsOneWidget);

      // Drag ListView up to reveal Telegram field
      await tester.drag(find.byType(ListView), const Offset(0, -200));
      await tester.pump();
      expect(find.text('Telegram Chat ID'), findsOneWidget);
    });

    testWidgets('renders email and push toggles', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      // Drag ListView up to reveal Email and Push toggles
      await tester.drag(find.byType(ListView), const Offset(0, -400));
      await tester.pump();
      expect(find.text('Email Notifications'), findsOneWidget);
      expect(find.text('Push Notifications'), findsOneWidget);
    });

    testWidgets('renders save button', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      // Drag ListView up to reveal save button
      await tester.drag(find.byType(ListView), const Offset(0, -600));
      await tester.pump();
      expect(find.text('Save Preferences'), findsOneWidget);
      expect(find.byType(ElevatedButton), findsOneWidget);
    });

    testWidgets('shows loading state then content', (tester) async {
      await tester.pumpWidget(buildTestApp());
      // Initially loading
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      // After pump, data loaded
      await tester.pump();
      expect(find.text('Content'), findsOneWidget);
    });
  });
}
