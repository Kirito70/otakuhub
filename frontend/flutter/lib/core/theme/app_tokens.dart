import 'dart:ui' show lerpDouble;

import 'package:flutter/material.dart';

/// ADR 094 — Design Tokens for OtakuHub.
///
/// Access via `Theme.of(context).extension<AppTokens>()!`.
/// Never hardcode hex values in widgets — always reference a token.
@immutable
class AppTokens extends ThemeExtension<AppTokens> {
  // ──────────────────────────────────────────────
  // Surface colors
  // ──────────────────────────────────────────────
  final Color bgBase;
  final Color bgSurface;
  final Color bgSurfaceAlt;
  final Color bgElevated;
  final Color bgHover;
  final Color borderSubtle;
  final Color borderStrong;

  // ──────────────────────────────────────────────
  // Text colors
  // ──────────────────────────────────────────────
  final Color textPrimary;
  final Color textSecondary;
  final Color textTertiary;
  final Color textOnAccent;

  // ──────────────────────────────────────────────
  // Brand & accent colors
  // ──────────────────────────────────────────────
  final Color accentPrimary;
  final Color accentPrimaryHover;
  final Color accentPrimaryPressed;
  final Color accentPrimarySubtle;
  final Color accentCoral;
  final Color accentMint;
  final Color accentCyan;
  final Color accentSky;
  final Color accentAmber;
  final Color accentRose;
  final Color accentGreen;

  // ──────────────────────────────────────────────
  // Spacing (4pt base)
  // ──────────────────────────────────────────────
  final double spaceXs;   //  4
  final double spaceSm;   //  8
  final double spaceMd;   // 16
  final double spaceLg;   // 24
  final double spaceXl;   // 32
  final double space2xl;  // 40
  final double space3xl;  // 56
  final double space4xl;  // 72

  // ──────────────────────────────────────────────
  // Border radius
  // ──────────────────────────────────────────────
  final double radiusSm;    // 10
  final double radiusMd;    // 14
  final double radiusLg;    // 20
  final double radiusXl;    // 28
  final double radiusPill;  // 999

  // ──────────────────────────────────────────────
  // Elevation shadows
  // ──────────────────────────────────────────────
  final List<BoxShadow> elevation1;
  final List<BoxShadow> elevation2;
  final List<BoxShadow> elevation3;

  // ──────────────────────────────────────────────
  // Brand gradient
  // ──────────────────────────────────────────────
  final Gradient brandGradient;

  // ──────────────────────────────────────────────
  // Constructor
  // ──────────────────────────────────────────────
  const AppTokens({
    required this.bgBase,
    required this.bgSurface,
    required this.bgSurfaceAlt,
    required this.bgElevated,
    required this.bgHover,
    required this.borderSubtle,
    required this.borderStrong,
    required this.textPrimary,
    required this.textSecondary,
    required this.textTertiary,
    required this.textOnAccent,
    required this.accentPrimary,
    required this.accentPrimaryHover,
    required this.accentPrimaryPressed,
    required this.accentPrimarySubtle,
    required this.accentCoral,
    required this.accentMint,
    required this.accentCyan,
    required this.accentSky,
    required this.accentAmber,
    required this.accentRose,
    required this.accentGreen,
    required this.spaceXs,
    required this.spaceSm,
    required this.spaceMd,
    required this.spaceLg,
    required this.spaceXl,
    required this.space2xl,
    required this.space3xl,
    required this.space4xl,
    required this.radiusSm,
    required this.radiusMd,
    required this.radiusLg,
    required this.radiusXl,
    required this.radiusPill,
    required this.elevation1,
    required this.elevation2,
    required this.elevation3,
    required this.brandGradient,
  });

  // ──────────────────────────────────────────────
  // Dark theme default
  // ──────────────────────────────────────────────
  static const AppTokens dark = AppTokens(
    // Surfaces
    bgBase: Color(0xFF0B0B12),
    bgSurface: Color(0xFF14141F),
    bgSurfaceAlt: Color(0xFF1A1A28),
    bgElevated: Color(0xFF1F1F30),
    bgHover: Color(0xFF26263A),
    borderSubtle: Color(0xFF262636),
    borderStrong: Color(0xFF3A3A52),

    // Text
    textPrimary: Color(0xFFF4F4F8),
    textSecondary: Color(0xFFA6A6BD),
    textTertiary: Color(0xFF6E6E85),
    textOnAccent: Color(0xFF0B0B12),

    // Accents
    accentPrimary: Color(0xFF7C5CFC),
    accentPrimaryHover: Color(0xFF8E72FF),
    accentPrimaryPressed: Color(0xFF6A48E0),
    accentPrimarySubtle: Color(0x247C5CFC), // 14% alpha
    accentCoral: Color(0xFFFF6E8A),
    accentMint: Color(0xFF2FD9A8),
    accentCyan: Color(0xFF3FD0D9),
    accentSky: Color(0xFF5AB0FF),
    accentAmber: Color(0xFFFFB454),
    accentRose: Color(0xFFFF5C6C),
    accentGreen: Color(0xFF7FD957),

    // Spacing
    spaceXs: 4,
    spaceSm: 8,
    spaceMd: 16,
    spaceLg: 24,
    spaceXl: 32,
    space2xl: 40,
    space3xl: 56,
    space4xl: 72,

    // Radius
    radiusSm: 10,
    radiusMd: 14,
    radiusLg: 20,
    radiusXl: 28,
    radiusPill: 999,

    // Elevation (dark UI = lighten surface + soft shadow)
    elevation1: [
      BoxShadow(
        offset: Offset(0, 2),
        blurRadius: 8,
        color: Color(0x59000000), // 35% alpha
      ),
    ],
    elevation2: [
      BoxShadow(
        offset: Offset(0, 8),
        blurRadius: 24,
        color: Color(0x73000000), // 45% alpha
      ),
    ],
    elevation3: [
      BoxShadow(
        offset: Offset(0, 16),
        blurRadius: 48,
        color: Color(0x8C000000), // 55% alpha
      ),
    ],

    // Brand gradient: violet → coral
    brandGradient: LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [Color(0xFF7C5CFC), Color(0xFFFF6E8A)],
    ),
  );

  // ──────────────────────────────────────────────
  // ThemeExtension required overrides
  // ──────────────────────────────────────────────
  @override
  AppTokens copyWith({
    Color? bgBase,
    Color? bgSurface,
    Color? bgSurfaceAlt,
    Color? bgElevated,
    Color? bgHover,
    Color? borderSubtle,
    Color? borderStrong,
    Color? textPrimary,
    Color? textSecondary,
    Color? textTertiary,
    Color? textOnAccent,
    Color? accentPrimary,
    Color? accentPrimaryHover,
    Color? accentPrimaryPressed,
    Color? accentPrimarySubtle,
    Color? accentCoral,
    Color? accentMint,
    Color? accentCyan,
    Color? accentSky,
    Color? accentAmber,
    Color? accentRose,
    Color? accentGreen,
    double? spaceXs,
    double? spaceSm,
    double? spaceMd,
    double? spaceLg,
    double? spaceXl,
    double? space2xl,
    double? space3xl,
    double? space4xl,
    double? radiusSm,
    double? radiusMd,
    double? radiusLg,
    double? radiusXl,
    double? radiusPill,
    List<BoxShadow>? elevation1,
    List<BoxShadow>? elevation2,
    List<BoxShadow>? elevation3,
    Gradient? brandGradient,
  }) {
    return AppTokens(
      bgBase: bgBase ?? this.bgBase,
      bgSurface: bgSurface ?? this.bgSurface,
      bgSurfaceAlt: bgSurfaceAlt ?? this.bgSurfaceAlt,
      bgElevated: bgElevated ?? this.bgElevated,
      bgHover: bgHover ?? this.bgHover,
      borderSubtle: borderSubtle ?? this.borderSubtle,
      borderStrong: borderStrong ?? this.borderStrong,
      textPrimary: textPrimary ?? this.textPrimary,
      textSecondary: textSecondary ?? this.textSecondary,
      textTertiary: textTertiary ?? this.textTertiary,
      textOnAccent: textOnAccent ?? this.textOnAccent,
      accentPrimary: accentPrimary ?? this.accentPrimary,
      accentPrimaryHover: accentPrimaryHover ?? this.accentPrimaryHover,
      accentPrimaryPressed: accentPrimaryPressed ?? this.accentPrimaryPressed,
      accentPrimarySubtle: accentPrimarySubtle ?? this.accentPrimarySubtle,
      accentCoral: accentCoral ?? this.accentCoral,
      accentMint: accentMint ?? this.accentMint,
      accentCyan: accentCyan ?? this.accentCyan,
      accentSky: accentSky ?? this.accentSky,
      accentAmber: accentAmber ?? this.accentAmber,
      accentRose: accentRose ?? this.accentRose,
      accentGreen: accentGreen ?? this.accentGreen,
      spaceXs: spaceXs ?? this.spaceXs,
      spaceSm: spaceSm ?? this.spaceSm,
      spaceMd: spaceMd ?? this.spaceMd,
      spaceLg: spaceLg ?? this.spaceLg,
      spaceXl: spaceXl ?? this.spaceXl,
      space2xl: space2xl ?? this.space2xl,
      space3xl: space3xl ?? this.space3xl,
      space4xl: space4xl ?? this.space4xl,
      radiusSm: radiusSm ?? this.radiusSm,
      radiusMd: radiusMd ?? this.radiusMd,
      radiusLg: radiusLg ?? this.radiusLg,
      radiusXl: radiusXl ?? this.radiusXl,
      radiusPill: radiusPill ?? this.radiusPill,
      elevation1: elevation1 ?? this.elevation1,
      elevation2: elevation2 ?? this.elevation2,
      elevation3: elevation3 ?? this.elevation3,
      brandGradient: brandGradient ?? this.brandGradient,
    );
  }

  @override
  AppTokens lerp(covariant AppTokens? other, double t) {
    if (other == null) return this;
    return AppTokens(
      bgBase: Color.lerp(bgBase, other.bgBase, t)!,
      bgSurface: Color.lerp(bgSurface, other.bgSurface, t)!,
      bgSurfaceAlt: Color.lerp(bgSurfaceAlt, other.bgSurfaceAlt, t)!,
      bgElevated: Color.lerp(bgElevated, other.bgElevated, t)!,
      bgHover: Color.lerp(bgHover, other.bgHover, t)!,
      borderSubtle: Color.lerp(borderSubtle, other.borderSubtle, t)!,
      borderStrong: Color.lerp(borderStrong, other.borderStrong, t)!,
      textPrimary: Color.lerp(textPrimary, other.textPrimary, t)!,
      textSecondary: Color.lerp(textSecondary, other.textSecondary, t)!,
      textTertiary: Color.lerp(textTertiary, other.textTertiary, t)!,
      textOnAccent: Color.lerp(textOnAccent, other.textOnAccent, t)!,
      accentPrimary: Color.lerp(accentPrimary, other.accentPrimary, t)!,
      accentPrimaryHover: Color.lerp(accentPrimaryHover, other.accentPrimaryHover, t)!,
      accentPrimaryPressed: Color.lerp(accentPrimaryPressed, other.accentPrimaryPressed, t)!,
      accentPrimarySubtle: Color.lerp(accentPrimarySubtle, other.accentPrimarySubtle, t)!,
      accentCoral: Color.lerp(accentCoral, other.accentCoral, t)!,
      accentMint: Color.lerp(accentMint, other.accentMint, t)!,
      accentCyan: Color.lerp(accentCyan, other.accentCyan, t)!,
      accentSky: Color.lerp(accentSky, other.accentSky, t)!,
      accentAmber: Color.lerp(accentAmber, other.accentAmber, t)!,
      accentRose: Color.lerp(accentRose, other.accentRose, t)!,
      accentGreen: Color.lerp(accentGreen, other.accentGreen, t)!,
      spaceXs: lerpDouble(spaceXs, other.spaceXs, t)!,
      spaceSm: lerpDouble(spaceSm, other.spaceSm, t)!,
      spaceMd: lerpDouble(spaceMd, other.spaceMd, t)!,
      spaceLg: lerpDouble(spaceLg, other.spaceLg, t)!,
      spaceXl: lerpDouble(spaceXl, other.spaceXl, t)!,
      space2xl: lerpDouble(space2xl, other.space2xl, t)!,
      space3xl: lerpDouble(space3xl, other.space3xl, t)!,
      space4xl: lerpDouble(space4xl, other.space4xl, t)!,
      radiusSm: lerpDouble(radiusSm, other.radiusSm, t)!,
      radiusMd: lerpDouble(radiusMd, other.radiusMd, t)!,
      radiusLg: lerpDouble(radiusLg, other.radiusLg, t)!,
      radiusXl: lerpDouble(radiusXl, other.radiusXl, t)!,
      radiusPill: lerpDouble(radiusPill, other.radiusPill, t)!,
      elevation1: other.elevation1,
      elevation2: other.elevation2,
      elevation3: other.elevation3,
      brandGradient: other.brandGradient,
    );
  }

  // ──────────────────────────────────────────────
  // Utility: watch-status → color
  // ──────────────────────────────────────────────
  Color statusColor(String status) {
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

  // ──────────────────────────────────────────────
  // Utility: score → color
  // ──────────────────────────────────────────────
  Color scoreColor(double? score) {
    if (score == null) return textTertiary;
    if (score >= 8.5) return accentMint;
    if (score >= 7.0) return accentGreen;
    if (score >= 5.5) return accentAmber;
    return accentRose;
  }

  // ──────────────────────────────────────────────
  // Utility: responsive edge padding
  // ──────────────────────────────────────────────
  EdgeInsets edgePadding(double screenWidth) {
    if (screenWidth < 600) {
      return EdgeInsets.all(spaceMd); // mobile: 16
    } else if (screenWidth < 1024) {
      return EdgeInsets.all(spaceLg); // tablet: 24
    }
    return EdgeInsets.all(space2xl); // desktop: 40
  }
}

/// Convenience extension to access AppTokens from BuildContext.
extension AppTokensExtension on BuildContext {
  AppTokens get tokens => Theme.of(this).extension<AppTokens>()!;
}
