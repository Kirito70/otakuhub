import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/core/auth/auth_provider.dart';
import 'package:otakuhub/features/auth/screens/setup_screen.dart';

/// A test double for AuthNotifier that allows controlling state and spying on calls.
class TestAuthNotifier extends AuthNotifier {
  AuthState _state = const AuthState();
  bool bootstrapCalled = false;
  String? bootstrapUsername;
  String? bootstrapEmail;
  String? bootstrapPassword;
  bool clearErrorCalled = false;

  void setState(AuthState newState) {
    _state = newState;
  }

  @override
  AuthState build() => _state;

  @override
  Future<void> bootstrapAdmin({
    required String username,
    required String email,
    required String password,
  }) async {
    bootstrapCalled = true;
    bootstrapUsername = username;
    bootstrapEmail = email;
    bootstrapPassword = password;
  }

  @override
  void clearError() {
    clearErrorCalled = true;
  }
}

Widget createTestApp(TestAuthNotifier notifier) {
  return ProviderScope(
    overrides: [
      authProvider.overrideWith(() => notifier),
    ],
    child: const MaterialApp(
      home: SetupScreen(),
    ),
  );
}

void main() {
  group('SetupScreen', () {
    testWidgets('renders welcome title and description', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.text('Welcome to OtakuHub'), findsOneWidget);
      expect(
        find.text('Create the first admin account to get started'),
        findsOneWidget,
      );
      expect(find.text('Create Admin Account'), findsOneWidget);
    });

    testWidgets('shows validation errors on empty submit', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.tap(find.text('Create Admin Account'));
      await tester.pumpAndSettle();

      expect(find.text('Username is required'), findsOneWidget);
      expect(find.text('Email is required'), findsOneWidget);
      expect(find.text('Password is required'), findsOneWidget);
      expect(find.text('Please confirm your password'), findsOneWidget);
    });

    testWidgets('validates minimum username length', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'ab');
      await tester.tap(find.text('Create Admin Account'));
      await tester.pumpAndSettle();

      expect(find.text('At least 3 characters'), findsOneWidget);
    });

    testWidgets('validates email format', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'admin');
      await tester.enterText(find.byType(TextFormField).at(1), 'invalid');
      await tester.tap(find.text('Create Admin Account'));
      await tester.pumpAndSettle();

      expect(find.text('Enter a valid email'), findsOneWidget);
    });

    testWidgets('validates minimum password length', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'admin');
      await tester.enterText(find.byType(TextFormField).at(1), 'admin@test.com');
      await tester.enterText(find.byType(TextFormField).at(2), 'short');
      await tester.tap(find.text('Create Admin Account'));
      await tester.pumpAndSettle();

      expect(find.text('At least 8 characters'), findsOneWidget);
    });

    testWidgets('validates password confirmation mismatch', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'admin');
      await tester.enterText(find.byType(TextFormField).at(1), 'admin@test.com');
      await tester.enterText(find.byType(TextFormField).at(2), 'password123');
      await tester.enterText(find.byType(TextFormField).at(3), 'different');
      await tester.tap(find.text('Create Admin Account'));
      await tester.pumpAndSettle();

      expect(find.text('Passwords do not match'), findsOneWidget);
    });

    testWidgets('calls bootstrapAdmin on valid form submission',
        (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(isLoading: false));

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'admin');
      await tester.enterText(find.byType(TextFormField).at(1), 'admin@test.com');
      await tester.enterText(find.byType(TextFormField).at(2), 'password123');
      await tester.enterText(find.byType(TextFormField).at(3), 'password123');
      await tester.tap(find.text('Create Admin Account'));
      await tester.pumpAndSettle();

      expect(notifier.clearErrorCalled, isTrue);
      expect(notifier.bootstrapCalled, isTrue);
      expect(notifier.bootstrapUsername, 'admin');
      expect(notifier.bootstrapEmail, 'admin@test.com');
      expect(notifier.bootstrapPassword, 'password123');
    });

    testWidgets('shows loading indicator when isLoading', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(isLoading: true));

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows error banner when error is set', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(error: 'Setup already completed'));

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.text('Setup already completed'), findsOneWidget);
    });

    testWidgets('toggles password visibility', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.byIcon(Icons.visibility_off_outlined), findsNWidgets(2));

      await tester.tap(find.byIcon(Icons.visibility_off_outlined).first);
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.visibility_outlined), findsOneWidget);
      expect(find.byIcon(Icons.visibility_off_outlined), findsOneWidget);
    });
  });
}
