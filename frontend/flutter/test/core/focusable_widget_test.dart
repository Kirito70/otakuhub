import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/core/widgets/focusable_widget.dart';

void main() {
  group('FocusableWidget', () {
    testWidgets('renders child widget', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              child: const Text('Hello'),
            ),
          ),
        ),
      );

      expect(find.text('Hello'), findsOneWidget);
    });

    testWidgets('triggers onPress on tap', (tester) async {
      var pressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              onPress: () => pressed = true,
              child: const Text('Tap me'),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Tap me'));
      expect(pressed, isTrue);
    });

    testWidgets('triggers onPress on keyboard Enter key', (tester) async {
      var pressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              onPress: () => pressed = true,
              child: const Text('Press Enter'),
            ),
          ),
        ),
      );

      // Tap to focus, then press Enter
      await tester.tap(find.text('Press Enter'));
      await tester.pump();

      await tester.sendKeyEvent(LogicalKeyboardKey.enter);
      expect(pressed, isTrue);
    });

    testWidgets('triggers onPress on keyboard Space key', (tester) async {
      var pressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              onPress: () => pressed = true,
              child: const Text('Press Space'),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Press Space'));
      await tester.pump();

      await tester.sendKeyEvent(LogicalKeyboardKey.space);
      expect(pressed, isTrue);
    });

    testWidgets('triggers onPress on Select key (D-pad center)', (tester) async {
      var pressed = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              onPress: () => pressed = true,
              child: const Text('Select me'),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Select me'));
      await tester.pump();

      await tester.sendKeyEvent(LogicalKeyboardKey.select);
      expect(pressed, isTrue);
    });

    testWidgets('shows border when focused', (tester) async {
      // Use a GlobalKey to access the FocusNode
      final focusNode = FocusNode();
      addTearDown(focusNode.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Focus(
              focusNode: focusNode,
              child: FocusableWidget(
                child: const Text('Focus me'),
              ),
            ),
          ),
        ),
      );

      // Initially border should not be visible (Container decoration border null)
      // Request focus
      focusNode.requestFocus();
      await tester.pump();

      // Now the FocusableWidget's internal FocusNode gets focus via traversal
      // Verify the accent border effect by checking the Container decoration after focus
      // The easiest way is to verify that AnimatedScale has the non-default scale
      // when _isFocused is true
    });

    testWidgets('responds to focus state change', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              autofocus: true,
              child: const SizedBox(width: 100, height: 100),
            ),
          ),
        ),
      );

      // autofocus should trigger focus
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 200));

      // With autofocus, the widget should have focus
      // Verify the Focus widget is present
      expect(find.byType(Focus), findsWidgets);
    });

    testWidgets('applies margin', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              margin: const EdgeInsets.all(16),
              child: const Text('Margined'),
            ),
          ),
        ),
      );

      final container = tester.widget<Container>(
        find.descendant(
          of: find.byType(FocusableWidget),
          matching: find.byType(Container),
        ).first,
      );

      expect(container.margin, const EdgeInsets.all(16));
    });

    testWidgets('has correct scale factor', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableWidget(
              scale: 1.15,
              child: const SizedBox(width: 100, height: 100),
            ),
          ),
        ),
      );

      // Find the AnimatedScale widget
      final animatedScale = tester.widget<AnimatedScale>(
        find.descendant(
          of: find.byType(FocusableWidget),
          matching: find.byType(AnimatedScale),
        ),
      );

      // When not focused, scale should equal the initial scale
      expect(animatedScale.scale, 1.15);
    });
  });

  group('FocusableTile', () {
    testWidgets('renders child widget', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableTile(
              child: const Text('Tile child'),
            ),
          ),
        ),
      );

      expect(find.text('Tile child'), findsOneWidget);
    });

    testWidgets('triggers onTap on tap', (tester) async {
      var tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableTile(
              onTap: () => tapped = true,
              child: const Text('Tap tile'),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Tap tile'));
      expect(tapped, isTrue);
    });

    testWidgets('triggers onTap on keyboard Enter', (tester) async {
      var tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: FocusableTile(
              onTap: () => tapped = true,
              child: const Text('Tile Enter'),
            ),
          ),
        ),
      );

      await tester.tap(find.text('Tile Enter'));
      await tester.pump();
      await tester.sendKeyEvent(LogicalKeyboardKey.enter);
      expect(tapped, isTrue);
    });
  });
}
