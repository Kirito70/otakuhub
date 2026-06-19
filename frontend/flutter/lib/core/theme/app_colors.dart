import 'package:flutter/material.dart';

/// ADR 094 — Color Palette.
///
/// This file provides the raw hex values grouped by role.
/// In widgets, always prefer `context.tokens.*` (from AppTokens ThemeExtension)
/// over these static constants, so theming is consistent and the light theme
/// can swap cleanly.
///
/// These static constants mirror [AppTokens.dark] for convenience / migration.
/// New code should use `Theme.of(context).extension<AppTokens>()!` exclusively.
class AppColors {
  AppColors._();

  // ── Surfaces ──────────────────────────────────
  static const Color bgBase = Color(0xFF0B0B12);
  static const Color bgSurface = Color(0xFF14141F);
  static const Color bgSurfaceAlt = Color(0xFF1A1A28);
  static const Color bgElevated = Color(0xFF1F1F30);
  static const Color bgHover = Color(0xFF26263A);
  static const Color borderSubtle = Color(0xFF262636);
  static const Color borderStrong = Color(0xFF3A3A52);

  // ── Text ──────────────────────────────────────
  static const Color textPrimary = Color(0xFFF4F4F8);
  static const Color textSecondary = Color(0xFFA6A6BD);
  static const Color textTertiary = Color(0xFF6E6E85);
  static const Color textOnAccent = Color(0xFF0B0B12);

  // ── Brand & accents ────────────────────────────
  static const Color accentPrimary = Color(0xFF7C5CFC);
  static const Color accentPrimaryHover = Color(0xFF8E72FF);
  static const Color accentPrimaryPressed = Color(0xFF6A48E0);
  static const Color accentPrimarySubtle = Color(0x247C5CFC);
  static const Color accentCoral = Color(0xFFFF6E8A);
  static const Color accentMint = Color(0xFF2FD9A8);
  static const Color accentCyan = Color(0xFF3FD0D9);
  static const Color accentSky = Color(0xFF5AB0FF);
  static const Color accentAmber = Color(0xFFFFB454);
  static const Color accentRose = Color(0xFFFF5C6C);
  static const Color accentGreen = Color(0xFF7FD957);

  // ── Brand gradient ─────────────────────────────
  static const Gradient brandGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [accentPrimary, accentCoral],
  );

  // ── Utility: status → color ────────────────────
  static Color statusColor(String status) {
    switch (status) {
      case 'watching':
      case 'reading':
        return accentMint;
      case 'rewatching':
      case 'rereading':
        return accentCyan;
      case 'completed':
        return accentPrimary;
      case 'plan_to_watch':
      case 'plan_to_read':
        return accentSky;
      case 'paused':
      case 'on_hold':
        return accentAmber;
      case 'dropped':
        return accentRose;
      default:
        return textTertiary;
    }
  }

  // ── Utility: score → color ─────────────────────
  static Color scoreColor(double? score) {
    if (score == null) return textTertiary;
    if (score >= 8.5) return accentMint;
    if (score >= 7.0) return accentGreen;
    if (score >= 5.5) return accentAmber;
    return accentRose;
  }

  // ── Backwards-compatible aliases ───────────────
  // These use the OLD hex values (pre-ADR 094) so screens that haven't been
  // redesigned yet look the same. Will be removed once all screens use
  // context.tokens. Defined as `static const` so they work in const contexts.
  static const Color bgPrimary = Color(0xFF0A0A0A);
  static const Color bgSecondary = Color(0xFF111111);
  static const Color borderDefault = Color(0xFF1F2937);
  static const Color accentSecondary = Color(0xFF06B6D4);
  static const Color textMuted = Color(0xFF6B7280);
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFEAB308);
  static const Color destructive = Color(0xFFEF4444);
  static const Color scoreGreen = Color(0xFF22C55E);
  static const Color scoreGold = Color(0xFFEAB308);
  static const Color scoreOrange = Color(0xFFF97316);
  static const Color scoreRed = Color(0xFFEF4444);
}
