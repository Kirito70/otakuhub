import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/tracking/widgets/progress_widget.dart';

void main() {
  group('ProgressWidget', () {
    testWidgets('renders current value', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ProgressWidget(
              value: 5,
              onChange: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('5'), findsOneWidget);
    });

    testWidgets('shows max when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ProgressWidget(
              value: 3,
              max: 12,
              onChange: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('/ 12'), findsOneWidget);
    });

    testWidgets('increment button works', (tester) async {
      int newValue = 0;
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ProgressWidget(
              value: 5,
              onChange: (v) => newValue = v,
            ),
          ),
        ),
      );

      // Find the + button (second Icon)
      final addButtons = find.byIcon(Icons.add);
      expect(addButtons, findsOneWidget);
      await tester.tap(addButtons);
      expect(newValue, 6);
    });

    testWidgets('decrement button works', (tester) async {
      int newValue = 0;
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ProgressWidget(
              value: 5,
              onChange: (v) => newValue = v,
            ),
          ),
        ),
      );

      final removeButtons = find.byIcon(Icons.remove);
      expect(removeButtons, findsOneWidget);
      await tester.tap(removeButtons);
      expect(newValue, 4);
    });

    testWidgets('decrement disabled at 0', (tester) async {
      bool changed = false;
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ProgressWidget(
              value: 0,
              onChange: (_) => changed = true,
            ),
          ),
        ),
      );

      final removeButtons = find.byIcon(Icons.remove);
      expect(removeButtons, findsOneWidget);
      await tester.tap(removeButtons);
      expect(changed, false);
    });
  });
}
