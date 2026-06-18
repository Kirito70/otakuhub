import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/profile/models/user_profile.dart';
import 'package:otakuhub/features/profile/providers/profile_provider.dart';
import 'package:otakuhub/features/profile/screens/profile_screen.dart';

void main() {
  final testProfile = UserProfile(
    id: '123',
    username: 'testuser',
    displayName: 'Test User',
    email: 'test@example.com',
    avatarUrl: 'https://example.com/avatar.png',
    bio: 'Anime lover',
    timezone: 'Asia/Tokyo',
    isActive: true,
    createdAt: DateTime(2024, 1, 15),
    updatedAt: DateTime(2025, 6, 1),
  );

  group('ProfileScreen data state', () {
    Widget buildTestApp() {
      return ProviderScope(
        overrides: [
          profileProvider.overrideWith((ref) async => testProfile),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const ProfileScreen(),
        ),
      );
    }

    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Profile'), findsOneWidget);
    });

    testWidgets('renders display name and username', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Test User'), findsOneWidget);
      expect(find.text('@testuser'), findsOneWidget);
    });

    testWidgets('renders email, timezone, and member since', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('test@example.com'), findsOneWidget);
      expect(find.text('Asia/Tokyo'), findsOneWidget);
      expect(find.textContaining('January 15, 2024'), findsOneWidget);
    });

    testWidgets('renders bio section', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Anime lover'), findsOneWidget);
    });

    testWidgets('renders action buttons', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Scroll down to find the action buttons
      await tester.dragUntilVisible(
        find.text('Edit Profile'),
        find.byType(ListView),
        const Offset(0, -200),
      );
      expect(find.text('Edit Profile'), findsOneWidget);
      expect(find.text('Account & Security'), findsOneWidget);
    });

    testWidgets('renders avatar', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // CircleAvatar with the network image should be rendered
      expect(find.byType(CircleAvatar), findsOneWidget);
    });
  });

  group('ProfileScreen no bio state', () {
    final profileNoBio = testProfile.copyWith(bio: null);

    Widget buildNoBioApp() {
      return ProviderScope(
        overrides: [
          profileProvider.overrideWith((ref) async => profileNoBio),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const ProfileScreen(),
        ),
      );
    }

    testWidgets('does not show bio section when bio is null', (tester) async {
      await tester.pumpWidget(buildNoBioApp());
      await tester.pumpAndSettle();

      expect(find.text('Bio'), findsNothing);
    });
  });

  group('ProfileScreen error state', () {
    Widget buildErrorApp() {
      return ProviderScope(
        overrides: [
          profileProvider.overrideWith((ref) async => throw Exception('Network error')),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const ProfileScreen(),
        ),
      );
    }

    testWidgets('shows error message and retry button', (tester) async {
      await tester.pumpWidget(buildErrorApp());
      await tester.pumpAndSettle();

      expect(find.text('Failed to load profile'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });
  });

  group('ProfileScreen username fallback', () {
    final profileNoDisplayName = testProfile.copyWith(displayName: null);

    Widget buildApp() {
      return ProviderScope(
        overrides: [
          profileProvider.overrideWith((ref) async => profileNoDisplayName),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const ProfileScreen(),
        ),
      );
    }

    testWidgets('falls back to username when no display name', (tester) async {
      await tester.pumpWidget(buildApp());
      await tester.pumpAndSettle();

      // Should show username as the title
      expect(find.text('testuser'), findsOneWidget);
      expect(find.text('@testuser'), findsOneWidget);
    });
  });
}
