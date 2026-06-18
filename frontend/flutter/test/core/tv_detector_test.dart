import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:otakuhub/core/platform/tv_detector.dart';

void main() {
  group('TVDetector', () {
    test('tvScale returns 1.15', () {
      expect(TVDetector.tvScale, 1.15);
    });

    test('gridColumns returns 5', () {
      expect(TVDetector.gridColumns, 5);
    });

    test('textScaleFactor returns 1.1', () {
      expect(TVDetector.textScaleFactor, 1.1);
    });

    testWidgets('isTV returns true for wide landscape (1920×1080)', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1920, 1080)),
            child: const _TvDetectorTestWidget(),
          ),
        ),
      );

      expect(find.text('TV: true'), findsOneWidget);
    });

    testWidgets('isTV returns false for phone (390×844)', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(size: Size(390, 844)),
            child: const _TvDetectorTestWidget(),
          ),
        ),
      );

      expect(find.text('TV: false'), findsOneWidget);
    });

    testWidgets('isTV returns false for tablet portrait (800×1280)', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(size: Size(800, 1280)),
            child: const _TvDetectorTestWidget(),
          ),
        ),
      );

      expect(find.text('TV: false'), findsOneWidget);
    });

    testWidgets('isTV returns false for window just below 1400', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1399, 900)),
            child: const _TvDetectorTestWidget(),
          ),
        ),
      );

      expect(find.text('TV: false'), findsOneWidget);
    });

    testWidgets('isTV returns true at exactly 1400 width with 1.5 ratio', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1400, 933)),
            child: const _TvDetectorTestWidget(),
          ),
        ),
      );

      expect(find.text('TV: true'), findsOneWidget);
    });

    testWidgets('isTV returns false for wide but short (1920×1440, ratio=1.33)', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1920, 1440)),
            child: const _TvDetectorTestWidget(),
          ),
        ),
      );

      expect(find.text('TV: false'), findsOneWidget);
    });
  });
}

/// Helper widget that displays "TV: true/false" based on [TVDetector.isTV].
class _TvDetectorTestWidget extends StatelessWidget {
  const _TvDetectorTestWidget();

  @override
  Widget build(BuildContext context) {
    final isTv = TVDetector.isTV(context);
    return Text('TV: $isTv');
  }
}
