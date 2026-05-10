---
paths:
  - "backend/tests/**"
  - "mobile/test/**"
  - "mobile/integration_test/**"
---
# Testing Rules

## Backend Tests (pytest)

### Required Tests Per Endpoint (minimum)
1. Success (200/201): valid input, authenticated
2. Unauthenticated (401): no token or expired token
3. Not found (404): valid UUID that doesn't exist in DB
4. Validation error (422): malformed request body

### Fixture Conventions
- `db_session`: fresh async test DB session per test
- `auth_headers`: `{"Authorization": "Bearer <test_token>"}`
- `seeded_<model>`: a real DB row created for the test
- `client`: `httpx.AsyncClient` with app + db_session override

### Anti-Patterns (never do these)
- Do NOT test implementation details — test HTTP behaviour
- Do NOT use production DB — always `TEST_DATABASE_URL`
- Do NOT mock SQLAlchemy internals — use real test DB
- Do NOT skip `downgrade()` in migration tests

## Flutter Tests (flutter_test + mocktail)

### Required Widget Tests Per Screen
1. Loading state: shows `CircularProgressIndicator`
2. Data state: shows key content widgets
3. Error state: shows `ErrorView` with retry button
4. Empty state (if applicable): shows empty state widget

### Provider Tests
- Mock the repository interface with `mocktail`
- Test: `build()` returns correct initial state
- Test: mutations update state correctly
- Test: errors are surfaced as `AsyncError`

### Test Utilities
```dart
// Wrap every widget test in ProviderScope
await tester.pumpWidget(
  ProviderScope(
    overrides: [
      myRepositoryProvider.overrideWith(() => MockMyRepository()),
    ],
    child: const MaterialApp(home: MyScreen()),
  ),
);
```

### Never
- Never access `AsyncValue.value` directly in tests — use `.when()` or `.requireValue`
- Never test GoRouter navigation without `RouterScope` wrapper
- Never use `find.byKey` unless the widget has a meaningful semantic key
