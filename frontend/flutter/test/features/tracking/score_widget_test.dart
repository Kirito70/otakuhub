import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/features/tracking/widgets/score_widget.dart';

void main() {
  group('ScoreWidget', () {
    testWidgets('renders empty stars when no value', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ScoreWidget(
              value: null,
              onChange: (_) {},
            ),
          ),
        ),
      );

      // Should show 5 empty stars
      expect(find.byIcon(Icons.star_border), findsNWidgets(5));
    });

    testWidgets('renders filled stars for score of 10', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ScoreWidget(
              value: 10,
              onChange: (_) {},
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.star), findsNWidgets(5));
      expect(find.text('10.0'), findsOneWidget);
    });

    testWidgets('renders half stars for score of 5', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ScoreWidget(
              value: 5,
              onChange: (_) {},
            ),
          ),
        ),
      );

      // 2 full stars (2,4) + 1 half star (5) + 2 empty (6,8,10)
      expect(find.byIcon(Icons.star), findsNWidgets(2));
      expect(find.byIcon(Icons.star_half), findsNWidgets(1));
      expect(find.byIcon(Icons.star_border), findsNWidgets(2));
      expect(find.text('5.0'), findsOneWidget);
    });

    testWidgets('tap toggles score on/off', (tester) async {
      double? newScore = 0;
      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: ScoreWidget(
              value: null,
              onChange: (v) => newScore = v,
            ),
          ),
        ),
      );

      // Tap the first star (sets score to 2)
      await tester.tap(find.byIcon(Icons.star_border).first);
      expect(newScore, 2.0);
    });
  });
}
