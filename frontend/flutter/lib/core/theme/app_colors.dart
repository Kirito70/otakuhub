import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  // Background
  static const Color bgPrimary = Color(0xFF0A0A0A);
  static const Color bgSecondary = Color(0xFF111111);
  static const Color bgElevated = Color(0xFF1A1A1A);

  // Accent
  static const Color accentPrimary = Color(0xFFA855F7); // Purple
  static const Color accentSecondary = Color(0xFF06B6D4); // Cyan

  // Text
  static const Color textPrimary = Color(0xFFFFFFFF);
  static const Color textSecondary = Color(0xFFA1A1AA);
  static const Color textMuted = Color(0xFF6B7280);

  // Borders
  static const Color borderDefault = Color(0xFF1F2937);
  static const Color borderStrong = Color(0xFF374151);

  // Status
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFEAB308);
  static const Color destructive = Color(0xFFEF4444);

  // Score thresholds
  static const Color scoreGreen = Color(0xFF22C55E);
  static const Color scoreGold = Color(0xFFEAB308);
  static const Color scoreOrange = Color(0xFFF97316);
  static const Color scoreRed = Color(0xFFEF4444);

  static Color scoreColor(double? score) {
    if (score == null) return textMuted;
    if (score >= 7.5) return scoreGreen;
    if (score >= 6.0) return scoreGold;
    if (score >= 4.0) return scoreOrange;
    return scoreRed;
  }
}
