import 'dart:async';

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

class _MockLoadingUpcoming extends UpcomingPartiesNotifier {
  @override
  Future<WatchPartyListResponse> build() async {
    // Never complete — simulate loading
    return Completer<WatchPartyListResponse>().future;
  }
}

void main() {
  group('WatchPartyScreen', () {
    Widget buildTestApp() {
      return ProviderScope(
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
          home: const WatchPartyScreen(),
        ),
      );
    }

    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Watch Party'), findsOneWidget);
    });

    testWidgets('renders all three tabs', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('Upcoming'), findsOneWidget);
      expect(find.text('Past'), findsOneWidget);
      expect(find.text('Create'), findsOneWidget);
      expect(find.byType(TabBar), findsOneWidget);
      expect(find.byType(TabBarView), findsOneWidget);
    });

    testWidgets('shows loading indicator initially', (tester) async {
      final container = ProviderScope(
        overrides: [
          upcomingPartiesNotifierProvider
              .overrideWith(() => _MockLoadingUpcoming()),
          pastPartiesNotifierProvider
              .overrideWith(() => _MockPastNotifier()),
          createPartyNotifierProvider
              .overrideWith(() => _MockCreateNotifier()),
          rsvpNotifierProvider.overrideWith(() => _MockRsvpNotifier()),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: WatchPartyScreen(),
        ),
      );

      await tester.pumpWidget(container);
      await tester.pump();

      // First tab (Upcoming) should show loading
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows empty state when no upcoming parties', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pump();

      expect(find.text('No upcoming parties'), findsOneWidget);
      expect(find.text('Create one to get started!'), findsOneWidget);
    });

    testWidgets('switching to Past tab shows empty state', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
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
            home: const WatchPartyScreen(initialTabIndex: 1),
          ),
        ),
      );
      await tester.pump();

      expect(find.text('No past parties'), findsOneWidget);
    });

    testWidgets('switching to Create tab shows form', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
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
        ),
      );
      await tester.pump();

      expect(find.text('New Watch Party'), findsOneWidget);
      expect(find.text('Create Party'), findsOneWidget);
    });
  });
}
