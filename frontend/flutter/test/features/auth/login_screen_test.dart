import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/core/auth/auth_provider.dart';
import 'package:otakuhub/features/auth/screens/login_screen.dart';

/// A test double for AuthNotifier that allows controlling state and spying on calls.
class TestAuthNotifier extends AuthNotifier {
  AuthState _state = const AuthState();
  bool loginCalled = false;
  String? loginUsername;
  String? loginPassword;
  bool clearErrorCalled = false;

  void setState(AuthState newState) {
    _state = newState;
  }

  @override
  AuthState build() => _state;

  @override
  Future<void> login(String username, String password) async {
    loginCalled = true;
    loginUsername = username;
    loginPassword = password;
  }

  @override
  void clearError() {
    clearErrorCalled = true;
    _state = _state.copyWith(error: null);
  }
}

Widget createTestApp(TestAuthNotifier notifier) {
  return ProviderScope(
    overrides: [
      authProvider.overrideWith(() => notifier),
    ],
    child: const MaterialApp(
      home: LoginScreen(),
    ),
  );
}

void main() {
  group('LoginScreen', () {
    testWidgets('renders title and subtitle', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.text('OtakuHub'), findsOneWidget);
      expect(find.text('Welcome back'), findsOneWidget);
      expect(find.text('Sign In'), findsOneWidget);
    });

    testWidgets('shows "Don\'t have an account? Sign Up" link',
        (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      // TextSpan inside Text.rich — use RichText widget predicate
      expect(
        find.byWidgetPredicate(
          (w) => w is RichText &&
              w.text.toPlainText().contains("Don't have an account? Sign Up"),
        ),
        findsOneWidget,
      );
    });

    testWidgets('shows validation errors on empty submit', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      expect(find.text('Username is required'), findsOneWidget);
      expect(find.text('Password is required'), findsOneWidget);
    });

    testWidgets('shows password error when only username is filled',
        (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).first, 'testuser');
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      expect(find.text('Username is required'), findsNothing);
      expect(find.text('Password is required'), findsOneWidget);
    });

    testWidgets('calls login on valid form submission', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(isLoading: false));

      await tester.pumpWidget(createTestApp(notifier));

      await tester.enterText(find.byType(TextFormField).first, 'testuser');
      await tester.enterText(find.byType(TextFormField).last, 'password123');
      await tester.tap(find.text('Sign In'));
      await tester.pumpAndSettle();

      expect(notifier.clearErrorCalled, isTrue);
      expect(notifier.loginCalled, isTrue);
      expect(notifier.loginUsername, 'testuser');
      expect(notifier.loginPassword, 'password123');
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
      notifier.setState(const AuthState(
        error: 'Invalid username or password',
      ));

      await tester.pumpWidget(createTestApp(notifier));

      expect(find.text('Invalid username or password'), findsOneWidget);
      expect(find.byIcon(Icons.close), findsOneWidget);
    });

    testWidgets('clears error when close icon is tapped', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState(
        error: 'Invalid username or password',
      ));

      await tester.pumpWidget(createTestApp(notifier));

      await tester.tap(find.byIcon(Icons.close));
      await tester.pumpAndSettle();

      expect(notifier.clearErrorCalled, isTrue);
    });

    testWidgets('toggles password visibility', (tester) async {
      final notifier = TestAuthNotifier();
      notifier.setState(const AuthState());

      await tester.pumpWidget(createTestApp(notifier));

      final passwordField = tester.widget<TextField>(
        find.byType(TextField).last,
      );
      expect(passwordField.obscureText, isTrue);

      await tester.tap(find.byIcon(Icons.visibility_off_outlined));
      await tester.pumpAndSettle();

      final passwordField2 = tester.widget<TextField>(
        find.byType(TextField).last,
      );
      expect(passwordField2.obscureText, isFalse);
    });
  });
}
