import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/profile/models/user_profile.dart';
import 'package:otakuhub/features/profile/providers/profile_provider.dart';
import 'package:otakuhub/features/profile/screens/edit_profile_screen.dart';

// Mock notifier that returns success without making API calls.
class _MockProfileUpdateNotifier extends ProfileUpdateNotifier {
  final UserProfile _profile;

  _MockProfileUpdateNotifier(this._profile);

  @override
  Future<UserProfile?> updateProfile(UserUpdate update) async {
    state = AsyncData(_profile);
    return _profile;
  }
}

// Mock notifier that returns failure without making API calls.
class _FailingProfileUpdateNotifier extends ProfileUpdateNotifier {
  @override
  Future<UserProfile?> updateProfile(UserUpdate update) async {
    state = AsyncError(Exception('Update failed'), StackTrace.current);
    return null;
  }
}

final UserProfile testProfile = UserProfile(
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

Widget buildTestApp({
  bool failingUpdate = false,
}) {
  return ProviderScope(
    overrides: [
      profileProvider.overrideWith((ref) async => testProfile),
      profileUpdateProvider.overrideWith(
        () => failingUpdate
            ? _FailingProfileUpdateNotifier()
            : _MockProfileUpdateNotifier(testProfile),
      ),
    ],
    child: MaterialApp(
      theme: ThemeData.dark(),
      home: const EditProfileScreen(),
    ),
  );
}

void main() {
  group('EditProfileScreen data state', () {
    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Edit Profile'), findsOneWidget);
    });

    testWidgets('pre-populates form fields from profile', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      final displayNameField = tester.widget<TextField>(
        find.byType(TextField).first,
      );
      expect(
        (displayNameField.controller)?.text,
        'Test User',
      );
    });

    testWidgets('renders save button', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Save Changes'), findsOneWidget);
    });
  });

  group('EditProfileScreen validation', () {
    testWidgets('shows validation error for invalid URL', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      final avatarField = find.byType(TextFormField).at(1);
      await tester.tap(avatarField);
      await tester.enterText(avatarField, 'not-a-url');

      await tester.tap(find.text('Save Changes'));
      await tester.pumpAndSettle();

      expect(find.text('Please enter a valid URL'), findsOneWidget);
    });

    testWidgets('saves with valid URL successfully', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      final avatarField = find.byType(TextFormField).at(1);
      await tester.tap(avatarField);
      await tester.enterText(avatarField, 'https://example.com/valid.png');

      await tester.tap(find.text('Save Changes'));
      await tester.pumpAndSettle();

      // Should show success message
      expect(
        find.text('Profile updated successfully.'),
        findsOneWidget,
      );
    });

    testWidgets('shows error on failed update', (tester) async {
      await tester.pumpWidget(buildTestApp(failingUpdate: true));
      await tester.pumpAndSettle();

      await tester.tap(find.text('Save Changes'));
      await tester.pumpAndSettle();

      // Should show error message
      expect(
        find.text('Failed to update profile. Please try again.'),
        findsOneWidget,
      );
    });
  });

  group('EditProfileScreen error state', () {
    Widget buildErrorApp() {
      return ProviderScope(
        overrides: [
          profileProvider.overrideWith(
            (ref) async => throw Exception('Failed to load'),
          ),
        ],
        child: MaterialApp(
          theme: ThemeData.dark(),
          home: const EditProfileScreen(),
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
}
