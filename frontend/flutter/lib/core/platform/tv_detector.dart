import 'package:flutter/material.dart';

/// TV form-factor detection and scaling constants.
///
/// Detection heuristic:
/// - Screen width >= 1400 logical pixels
/// - Aspect ratio >= 1.5 (landscape profile typical of TVs)
///
/// This heuristic works for Android TV, Fire TV, and other TV platforms.
/// Desktop monitors with similar dimensions will also match, which is
/// acceptable — TV mode is backward-compatible with keyboard navigation.
class TVDetector {
  TVDetector._();

  /// Whether the current [BuildContext] indicates a TV form factor.
  static bool isTV(BuildContext context) {
    final size = MediaQuery.of(context).size;
    final aspectRatio = size.width / size.height;
    return size.width >= 1400 && aspectRatio >= 1.5;
  }

  /// Scale multiplier for TV-targeted UI (1.15× for readability at distance).
  static double get tvScale => 1.15;

  /// Number of grid columns for TV content layouts.
  static int get gridColumns => 5;

  /// Text scale factor for TV readability.
  static double get textScaleFactor => 1.1;
}
