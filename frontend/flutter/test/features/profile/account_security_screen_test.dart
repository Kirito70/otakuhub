import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/profile/models/user_profile.dart';
import 'package:otakuhub/features/profile/providers/profile_provider.dart';
import 'package:otakuhub/features/profile/screens/account_security_screen.dart';

// Mock notifier that returns success for password change.
class _MockPasswordChangeNotifier extends PasswordChangeNotifier {
  @override
  Future<bool?> changePassword(ChangePasswordRequest request) async {
    state = const AsyncData(true);
    return true;
  }
}

// Mock notifier that returns failure for password change.
class _FailingPasswordChangeNotifier extends PasswordChangeNotifier {
  @override
  Future<bool?> changePassword(ChangePasswordRequest request) async {
    state = AsyncError(Exception('Change failed'), StackTrace.current);
    return null;
  }
}

Widget buildTestApp({bool failing = false}) {
  return ProviderScope(
    overrides: [
      passwordChangeProvider.overrideWith(
        () => failing
            ? _FailingPasswordChangeNotifier()
            : _MockPasswordChangeNotifier(),
      ),
    ],
    child: MaterialApp(
      theme: ThemeData.dark(),
      home: const AccountSecurityScreen(),
    ),
  );
}

void main() {
  group('AccountSecurityScreen data state', () {
    testWidgets('renders app bar title', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Account & Security'), findsOneWidget);
    });

    testWidgets('renders password info card', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Password'), findsOneWidget);
      expect(
        find.textContaining('Use at least 8 characters'),
        findsOneWidget,
      );
    });

    testWidgets('renders all three password fields', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Current Password'), findsOneWidget);
      expect(find.text('New Password'), findsOneWidget);
      expect(find.text('Confirm New Password'), findsOneWidget);
    });

    testWidgets('renders change password button', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      expect(find.text('Change Password'), findsOneWidget);
    });
  });

  group('AccountSecurityScreen validation', () {
    testWidgets('shows validation errors on empty submit', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Tap submit with empty fields
      await tester.tap(find.text('Change Password'));
      await tester.pumpAndSettle();

      expect(find.text('Current password is required'), findsOneWidget);
      expect(find.text('New password is required'), findsOneWidget);
      expect(find.text('Please confirm your new password'), findsOneWidget);
    });

    testWidgets('shows error for short new password', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Fill current password
      await tester.enterText(
        find.byType(TextFormField).at(0),
        'currentPass123',
      );
      // Enter short new password
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'short',
      );

      await tester.tap(find.text('Change Password'));
      await tester.pumpAndSettle();

      expect(
        find.text('Password must be at least 8 characters'),
        findsOneWidget,
      );
    });

    testWidgets('shows error for mismatched passwords', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Fill current password
      await tester.enterText(
        find.byType(TextFormField).at(0),
        'currentPass123',
      );
      // Enter new password
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'newPass12345',
      );
      // Enter different confirm password
      await tester.enterText(
        find.byType(TextFormField).at(2),
        'differentPass',
      );

      await tester.tap(find.text('Change Password'));
      await tester.pumpAndSettle();

      expect(find.text('Passwords do not match'), findsOneWidget);
    });

    testWidgets('submits successfully with valid data', (tester) async {
      await tester.pumpWidget(buildTestApp());
      await tester.pumpAndSettle();

      // Fill all fields
      await tester.enterText(
        find.byType(TextFormField).at(0),
        'currentPass123',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'newStrongPass1',
      );
      await tester.enterText(
        find.byType(TextFormField).at(2),
        'newStrongPass1',
      );

      await tester.tap(find.text('Change Password'));
      await tester.pumpAndSettle();

      expect(
        find.text('Password changed successfully.'),
        findsOneWidget,
      );
    });

    testWidgets('shows error on failed password change', (tester) async {
      await tester.pumpWidget(buildTestApp(failing: true));
      await tester.pumpAndSettle();

      // Fill all fields
      await tester.enterText(
        find.byType(TextFormField).at(0),
        'wrongCurrentPass',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'newStrongPass1',
      );
      await tester.enterText(
        find.byType(TextFormField).at(2),
        'newStrongPass1',
      );

      await tester.tap(find.text('Change Password'));
      await tester.pumpAndSettle();

      expect(
        find.textContaining('Failed to change password'),
        findsOneWidget,
      );
    });
  });
}
