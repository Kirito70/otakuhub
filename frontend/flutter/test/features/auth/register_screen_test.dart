import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/core/auth/auth_provider.dart';
import 'package:otakuhub/features/auth/screens/register_screen.dart';

/// A test double for AuthNotifier that allows controlling state and spying on calls.
class TestAuthNotifier extends AuthNotifier {
  AuthState _state = const AuthState();
  bool registerCalled = false;
  String? registerUsername;
  String? registerEmail;
  String? registerPassword;
  bool clearErrorCalled = false;

  void setState(AuthState newState) {
    _state = newState;
  }

  @override
  AuthState build() => _state;

  @override
  Future<void> register(String username, String email, String password) async {
    registerCalled = true;
    registerUsername = username;
    registerEmail = email;
    registerPassword = password;
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
      home: RegisterScreen(),
    ),
  );
}

void main() {
  group('RegisterScreen', () {
    testWidgets('renders title and create button', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.text('Create Account'), findsNWidgets(2));
      // TextSpan inside Text.rich — use RichText widget predicate
      expect(
        find.byWidgetPredicate(
          (w) => w is RichText &&
              w.text.toPlainText().contains('Already have an account? Sign In'),
        ),
        findsOneWidget,
      );
    });

    testWidgets('shows validation errors on empty submit', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.tap(find.text('Create Account').last);
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
      await tester.tap(find.text('Create Account').last);
      await tester.pumpAndSettle();

      expect(find.text('At least 3 characters'), findsOneWidget);
    });

    testWidgets('validates email format', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'testuser');
      await tester.enterText(find.byType(TextFormField).at(1), 'notanemail');
      await tester.tap(find.text('Create Account').last);
      await tester.pumpAndSettle();

      expect(find.text('Enter a valid email'), findsOneWidget);
    });

    testWidgets('validates minimum password length', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'testuser');
      await tester.enterText(find.byType(TextFormField).at(1), 'user@test.com');
      await tester.enterText(find.byType(TextFormField).at(2), 'short');
      await tester.tap(find.text('Create Account').last);
      await tester.pumpAndSettle();

      expect(find.text('At least 8 characters'), findsOneWidget);
    });

    testWidgets('validates password confirmation mismatch', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'testuser');
      await tester.enterText(find.byType(TextFormField).at(1), 'user@test.com');
      await tester.enterText(find.byType(TextFormField).at(2), 'password123');
      await tester.enterText(find.byType(TextFormField).at(3), 'different');
      await tester.tap(find.text('Create Account').last);
      await tester.pumpAndSettle();

      expect(find.text('Passwords do not match'), findsOneWidget);
    });

    testWidgets('calls register on valid form submission', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(isLoading: false));

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).at(0), 'testuser');
      await tester.enterText(find.byType(TextFormField).at(1), 'user@test.com');
      await tester.enterText(find.byType(TextFormField).at(2), 'password123');
      await tester.enterText(find.byType(TextFormField).at(3), 'password123');
      await tester.tap(find.text('Create Account').last);
      await tester.pumpAndSettle();

      expect(notifier.clearErrorCalled, isTrue);
      expect(notifier.registerCalled, isTrue);
      expect(notifier.registerUsername, 'testuser');
      expect(notifier.registerEmail, 'user@test.com');
      expect(notifier.registerPassword, 'password123');
    });

    testWidgets('shows loading indicator when isLoading', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(isLoading: true));

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      final button =
          tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.onPressed, isNull);
    });

    testWidgets('shows error banner when error is set', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(error: 'User already exists'));

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.text('User already exists'), findsOneWidget);
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
