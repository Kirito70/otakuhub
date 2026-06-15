import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/watchparty/models/watch_party.dart';
import 'package:otakuhub/features/watchparty/providers/watch_party_provider.dart';
import 'package:otakuhub/features/watchparty/widgets/party_detail_sheet.dart';

// --- Sample data ---

final _sampleDetail = WatchPartyDetail(
  id: 'party-1',
  groupId: 'group-1',
  hostUserId: 'user-1',
  hostUsername: 'tayyab',
  hostDisplayName: 'Tayyab',
  mediaId: 'media-1',
  mediaTitle: 'Solo Leveling',
  episodeNumber: 12,
  title: 'Solo Leveling Watch Party',
  scheduledAt: DateTime(2026, 6, 20, 20, 0),
  status: 'scheduled',
  createdAt: DateTime(2026, 6, 16),
  updatedAt: DateTime(2026, 6, 16),
  attendeeCount: 3,
);

final _sampleRsvpList = WatchPartyRsvpListResponse(
  items: [
    WatchPartyRsvp(
      partyId: 'party-1',
      userId: 'user-1',
      status: 'attending',
      createdAt: DateTime(2026, 6, 16),
    ),
    WatchPartyRsvp(
      partyId: 'party-1',
      userId: 'user-2',
      status: 'pending',
      createdAt: DateTime(2026, 6, 16),
    ),
  ],
  total: 2,
);

void main() {
  group('PartyDetailSheet', () {
    Widget buildTestApp({
      required WatchPartyDetail detail,
      required WatchPartyRsvpListResponse rsvps,
    }) {
      return ProviderScope(
        overrides: [
          partyDetailProviderProvider('party-1')
              .overrideWith((ref) async => detail),
          partyRsvpsProviderProvider('party-1')
              .overrideWith((ref) async => rsvps),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: Builder(
              builder: (context) => ElevatedButton(
                onPressed: () {
                  showModalBottomSheet<dynamic>(
                    context: context,
                    isScrollControlled: true,
                    backgroundColor: Colors.transparent,
                    builder: (_) =>
                        const PartyDetailSheet(partyId: 'party-1'),
                  );
                },
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      );
    }

    testWidgets('detail sheet loads and shows title', (tester) async {
      await tester.pumpWidget(buildTestApp(
        detail: _sampleDetail,
        rsvps: _sampleRsvpList,
      ));
      await tester.pump();

      // Tap button to open sheet
      await tester.tap(find.text('Open'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 500));

      expect(find.text('Solo Leveling Watch Party'), findsOneWidget);
    });

    testWidgets('detail sheet shows host info', (tester) async {
      await tester.pumpWidget(buildTestApp(
        detail: _sampleDetail,
        rsvps: _sampleRsvpList,
      ));
      await tester.pump();

      await tester.tap(find.text('Open'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 500));

      expect(find.text('Hosted by'), findsOneWidget);
      expect(find.text('Tayyab'), findsOneWidget);
    });

    testWidgets('detail sheet shows RSVP buttons', (tester) async {
      await tester.pumpWidget(buildTestApp(
        detail: _sampleDetail,
        rsvps: _sampleRsvpList,
      ));
      await tester.pump();

      await tester.tap(find.text('Open'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 500));

      expect(find.text('Your RSVP'), findsOneWidget);
      expect(find.text('Attending'), findsOneWidget);
      expect(find.text('Maybe'), findsOneWidget);
      expect(find.text('Decline'), findsOneWidget);
    });

    testWidgets('detail sheet shows attendee section header',
        (tester) async {
      await tester.pumpWidget(buildTestApp(
        detail: _sampleDetail,
        rsvps: _sampleRsvpList,
      ));
      await tester.pump();

      await tester.tap(find.text('Open'));
      await tester.pump();
      // Step through modal sheet animation
      for (int i = 0; i < 10; i++) {
        await tester.pump(const Duration(milliseconds: 50));
      }

      // Scroll down in the DraggableScrollableSheet to see Attendees section
      await tester.drag(
        find.byType(ListView).first,
        const Offset(0, -400),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 300));

      expect(find.text('Attendees'), findsOneWidget);
    });
  });
}
