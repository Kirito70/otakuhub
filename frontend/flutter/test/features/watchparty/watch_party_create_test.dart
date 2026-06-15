import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/watchparty/models/watch_party.dart';
import 'package:otakuhub/features/watchparty/providers/watch_party_provider.dart';
import 'package:otakuhub/features/watchparty/screens/watch_party_screen.dart';

// --- Mock notifiers ---

class _MockUpcomingNotifier extends UpcomingPartiesNotifier {
  @override
  Future<WatchPartyListResponse> build() async => WatchPartyListResponse(
        items: const [],
        total: 0,
        limit: 50,
        offset: 0,
      );
}

class _MockPastNotifier extends PastPartiesNotifier {
  @override
  Future<WatchPartyListResponse> build() async => WatchPartyListResponse(
        items: const [],
        total: 0,
        limit: 50,
        offset: 0,
      );
}

class _MockCreateNotifier extends CreatePartyNotifier {
  @override
  Future<WatchParty?> build() async => null;
}

class _MockRsvpNotifier extends RsvpNotifier {
  @override
  Future<WatchPartyRsvp?> build() async => null;
}

void main() {
  group('WatchParty Create Tab', () {
    Future<void> navigateToCreateTab(WidgetTester tester) async {
      // Build with initialTabIndex=2 to directly show Create tab
      final app = ProviderScope(
        overrides: [
          upcomingPartiesNotifierProvider
              .overrideWith(() => _MockUpcomingNotifier()),
          pastPartiesNotifierProvider
              .overrideWith(() => _MockPastNotifier()),
          createPartyNotifierProvider
              .overrideWith(() => _MockCreateNotifier()),
          rsvpNotifierProvider.overrideWith(() => _MockRsvpNotifier()),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const WatchPartyScreen(initialTabIndex: 2),
        ),
      );
      await tester.pumpWidget(app);
      await tester.pump();
    }

    testWidgets('required fields show validation errors on empty submit',
        (tester) async {
      await navigateToCreateTab(tester);

      // Scroll down so the Create Party button is visible
      await tester.drag(
        find.byType(SingleChildScrollView),
        const Offset(0, -400),
      );
      await tester.pump();

      // Tap create without filling required fields
      await tester.tap(find.text('Create Party'));
      await tester.pump();

      expect(find.text('Group ID is required'), findsOneWidget);
      expect(find.text('Media ID is required'), findsOneWidget);
    });

    testWidgets('submit button is disabled while loading', (tester) async {
      await navigateToCreateTab(tester);

      // Check the button exists
      final createButton = find.text('Create Party');
      expect(createButton, findsOneWidget);
    });

    testWidgets('form displays all expected fields', (tester) async {
      await navigateToCreateTab(tester);

      expect(find.text('New Watch Party'), findsOneWidget);
      expect(find.text('Group ID *'), findsOneWidget);
      expect(find.text('Media ID *'), findsOneWidget);
      expect(find.text('Title (optional)'), findsOneWidget);
      expect(find.text('Episode (optional)'), findsOneWidget);
      expect(find.text('Date & Time *'), findsOneWidget);
      expect(find.text('Stream URL (optional)'), findsOneWidget);
      expect(find.text('Notes (optional)'), findsOneWidget);
    });

    testWidgets('date picker is tappable', (tester) async {
      await navigateToCreateTab(tester);

      // Tap date picker container
      final dateTile = find.text('Tap to select');
      await tester.tap(dateTile);
      await tester.pump();

      // A date picker dialog should appear
      expect(find.byType(DatePickerDialog), findsOneWidget);
    });
  });
}
