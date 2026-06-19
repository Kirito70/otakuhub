import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — AppTheme builds the complete Material 3 dark ThemeData using
/// design tokens from [AppTokens] and typography from [google_fonts].
///
/// Widgets access tokens via `context.tokens` (see [AppTokensExtension]).
class AppTheme {
  AppTheme._();

  /// The single dark theme. Every visual element is driven by [AppTokens.dark].
  static ThemeData get dark {
    final tokens = AppTokens.dark;

    // ── ColorScheme (M3) ──────────────────────────
    // Build from seed then override key slots with exact token values.
    final colorScheme = ColorScheme.fromSeed(
      seedColor: tokens.accentPrimary,
      brightness: Brightness.dark,
    ).copyWith(
      primary: tokens.accentPrimary,
      onPrimary: tokens.textOnAccent,
      primaryContainer: tokens.accentPrimarySubtle,
      secondary: tokens.accentCoral,
      onSecondary: tokens.textOnAccent,
      surface: tokens.bgSurface,
      surfaceContainerHighest: tokens.bgSurfaceAlt,
      onSurface: tokens.textPrimary,
      onSurfaceVariant: tokens.textSecondary,
      error: tokens.accentRose,
      onError: tokens.textOnAccent,
      outline: tokens.borderSubtle,
      outlineVariant: tokens.borderStrong,
    );

    // ── Typography ────────────────────────────────
    final textTheme = TextTheme(
      displayLarge: GoogleFonts.spaceGrotesk(
        fontSize: 40,
        height: 46 / 40,
        fontWeight: FontWeight.w700,
        color: tokens.textPrimary,
      ),
      displayMedium: GoogleFonts.spaceGrotesk(
        fontSize: 30,
        height: 36 / 30,
        fontWeight: FontWeight.w700,
        color: tokens.textPrimary,
      ),
      headlineLarge: GoogleFonts.spaceGrotesk(
        fontSize: 24,
        height: 30 / 24,
        fontWeight: FontWeight.w600,
        color: tokens.textPrimary,
      ),
      titleLarge: GoogleFonts.plusJakartaSans(
        fontSize: 20,
        height: 26 / 20,
        fontWeight: FontWeight.w600,
        color: tokens.textPrimary,
      ),
      titleMedium: GoogleFonts.plusJakartaSans(
        fontSize: 17,
        height: 22 / 17,
        fontWeight: FontWeight.w600,
        color: tokens.textPrimary,
      ),
      bodyLarge: GoogleFonts.plusJakartaSans(
        fontSize: 15,
        height: 22 / 15,
        fontWeight: FontWeight.w400,
        color: tokens.textPrimary,
      ),
      bodyMedium: GoogleFonts.plusJakartaSans(
        fontSize: 14,
        height: 20 / 14,
        fontWeight: FontWeight.w400,
        color: tokens.textSecondary,
      ),
      labelLarge: GoogleFonts.plusJakartaSans(
        fontSize: 13,
        height: 16 / 13,
        fontWeight: FontWeight.w600,
        color: tokens.textPrimary,
      ),
      bodySmall: GoogleFonts.plusJakartaSans(
        fontSize: 12,
        height: 16 / 12,
        fontWeight: FontWeight.w400,
        color: tokens.textTertiary,
      ),
      labelSmall: GoogleFonts.plusJakartaSans(
        fontSize: 11,
        height: 14 / 11,
        fontWeight: FontWeight.w600,
        color: tokens.textSecondary,
      ),
    );

    // ── ThemeData ─────────────────────────────────
    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: tokens.bgBase,

      // Typography
      textTheme: textTheme,

      // Custom tokens exposed via ThemeExtension
      extensions: const <ThemeExtension<dynamic>>[AppTokens.dark],

      // ── AppBar ──────────────────────────────────
      appBarTheme: AppBarTheme(
        backgroundColor: Colors.transparent,
        foregroundColor: tokens.textPrimary,
        elevation: 0,
        centerTitle: false,
        scrolledUnderElevation: 0,
        titleTextStyle: GoogleFonts.plusJakartaSans(
          fontSize: 18,
          fontWeight: FontWeight.w600,
          color: tokens.textPrimary,
        ),
      ),

      // ── Cards ───────────────────────────────────
      cardTheme: CardThemeData(
        color: tokens.bgSurface,
        elevation: 0,
        shadowColor: Colors.black,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusLg)),
          side: BorderSide(color: tokens.borderSubtle),
        ),
        clipBehavior: Clip.antiAlias,
        margin: EdgeInsets.zero,
      ),

      // ── Buttons ─────────────────────────────────
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: tokens.accentPrimary,
          foregroundColor: tokens.textOnAccent,
          elevation: 0,
          shadowColor: Colors.transparent,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          minimumSize: const Size(0, 44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(tokens.radiusPill)),
          ),
          textStyle: GoogleFonts.plusJakartaSans(
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: tokens.accentPrimary,
          foregroundColor: tokens.textOnAccent,
          minimumSize: const Size(0, 44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(tokens.radiusPill)),
          ),
          textStyle: GoogleFonts.plusJakartaSans(
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: tokens.accentPrimary,
          minimumSize: const Size(0, 44),
          textStyle: GoogleFonts.plusJakartaSans(
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: tokens.textPrimary,
          side: BorderSide(color: tokens.borderSubtle),
          minimumSize: const Size(0, 44),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
          ),
          textStyle: GoogleFonts.plusJakartaSans(
            fontSize: 13,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),

      // ── Input fields ────────────────────────────
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: tokens.bgSurfaceAlt,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 14,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
          borderSide: BorderSide(color: tokens.borderSubtle),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
          borderSide: BorderSide(color: tokens.borderSubtle),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
          borderSide: BorderSide(color: tokens.accentPrimary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
          borderSide: BorderSide(color: tokens.accentRose),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
          borderSide: BorderSide(color: tokens.accentRose, width: 2),
        ),
        labelStyle: TextStyle(color: tokens.textSecondary),
        hintStyle: TextStyle(color: tokens.textTertiary),
        errorStyle: TextStyle(color: tokens.accentRose),
      ),

      // ── Navigation ──────────────────────────────
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: tokens.bgElevated,
        indicatorColor: tokens.accentPrimarySubtle,
        surfaceTintColor: Colors.transparent,
        elevation: 8,
        shadowColor: Colors.black,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return GoogleFonts.plusJakartaSans(
              color: tokens.accentPrimary,
              fontSize: 11,
              fontWeight: FontWeight.w600,
            );
          }
          return GoogleFonts.plusJakartaSans(
            color: tokens.textTertiary,
            fontSize: 11,
            fontWeight: FontWeight.w500,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return IconThemeData(color: tokens.accentPrimary, size: 24);
          }
          return IconThemeData(color: tokens.textTertiary, size: 24);
        }),
      ),
      navigationRailTheme: NavigationRailThemeData(
        backgroundColor: tokens.bgBase,
        indicatorColor: tokens.accentPrimarySubtle,
        labelType: NavigationRailLabelType.all,
        selectedLabelTextStyle: GoogleFonts.plusJakartaSans(
          color: tokens.accentPrimary,
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelTextStyle: GoogleFonts.plusJakartaSans(
          color: tokens.textTertiary,
          fontSize: 11,
          fontWeight: FontWeight.w500,
        ),
        selectedIconTheme: IconThemeData(
          color: tokens.accentPrimary,
          size: 24,
        ),
        unselectedIconTheme: IconThemeData(
          color: tokens.textTertiary,
          size: 24,
        ),
      ),

      // ── Bottom sheet ────────────────────────────
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: tokens.bgElevated,
        surfaceTintColor: Colors.transparent,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        ),
        modalBarrierColor: Colors.black54,
        elevation: 16,
        shadowColor: Colors.black,
      ),

      // ── Dialog ──────────────────────────────────
      dialogTheme: DialogThemeData(
        backgroundColor: tokens.bgElevated,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusXl)),
        ),
      ),

      // ── Divider ─────────────────────────────────
      dividerTheme: DividerThemeData(
        color: tokens.borderSubtle,
        thickness: 1,
        space: 1,
      ),

      // ── Chip ────────────────────────────────────
      chipTheme: ChipThemeData(
        backgroundColor: tokens.bgSurfaceAlt,
        selectedColor: tokens.accentPrimarySubtle,
        labelStyle: GoogleFonts.plusJakartaSans(
          color: tokens.textSecondary,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
        secondaryLabelStyle: GoogleFonts.plusJakartaSans(
          color: tokens.accentPrimary,
          fontSize: 12,
          fontWeight: FontWeight.w600,
        ),
        side: BorderSide(color: tokens.borderSubtle),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusPill)),
        ),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      ),

      // ── Progress indicator ──────────────────────
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: tokens.accentPrimary,
        linearTrackColor: tokens.bgSurfaceAlt,
        circularTrackColor: tokens.bgSurfaceAlt,
      ),

      // ── Snackbar ────────────────────────────────
      snackBarTheme: SnackBarThemeData(
        backgroundColor: tokens.bgElevated,
        contentTextStyle: GoogleFonts.plusJakartaSans(
          color: tokens.textPrimary,
          fontSize: 14,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusLg)),
        ),
        behavior: SnackBarBehavior.floating,
        actionTextColor: tokens.accentPrimary,
      ),

      // ── Tabs ────────────────────────────────────
      tabBarTheme: TabBarThemeData(
        labelColor: tokens.accentPrimary,
        unselectedLabelColor: tokens.textTertiary,
        indicatorColor: tokens.accentPrimary,
        labelStyle: GoogleFonts.plusJakartaSans(
          fontSize: 13,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: GoogleFonts.plusJakartaSans(
          fontSize: 13,
          fontWeight: FontWeight.w500,
        ),
      ),

      // ── Tooltip ─────────────────────────────────
      tooltipTheme: TooltipThemeData(
        decoration: BoxDecoration(
          color: tokens.bgElevated,
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusSm)),
        ),
        textStyle: GoogleFonts.plusJakartaSans(
          fontSize: 12,
          color: tokens.textPrimary,
        ),
      ),

      // ── Popup menu ──────────────────────────────
      popupMenuTheme: PopupMenuThemeData(
        color: tokens.bgElevated,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
        ),
        elevation: 8,
        textStyle: GoogleFonts.plusJakartaSans(
          fontSize: 14,
          color: tokens.textPrimary,
        ),
      ),

      // ── Floating action button ──────────────────
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: tokens.accentPrimary,
        foregroundColor: tokens.textOnAccent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusPill)),
        ),
        elevation: 4,
        extendedTextStyle: GoogleFonts.plusJakartaSans(
          fontSize: 13,
          fontWeight: FontWeight.w600,
        ),
      ),

      // ── Scrollbar ───────────────────────────────
      scrollbarTheme: ScrollbarThemeData(
        thumbColor: WidgetStatePropertyAll(tokens.borderStrong),
        trackColor: WidgetStatePropertyAll(Colors.transparent),
        radius: Radius.circular(tokens.radiusPill),
        thickness: WidgetStatePropertyAll(4),
      ),

      // ── List tiles ──────────────────────────────
      listTileTheme: ListTileThemeData(
        tileColor: Colors.transparent,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16),
        titleTextStyle: GoogleFonts.plusJakartaSans(
          fontSize: 15,
          fontWeight: FontWeight.w500,
          color: tokens.textPrimary,
        ),
        subtitleTextStyle: GoogleFonts.plusJakartaSans(
          fontSize: 13,
          color: tokens.textSecondary,
        ),
        leadingAndTrailingTextStyle: GoogleFonts.plusJakartaSans(
          fontSize: 13,
          fontWeight: FontWeight.w600,
          color: tokens.textSecondary,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
        ),
      ),

      // ── Switch ──────────────────────────────────
      switchTheme: SwitchThemeData(
        thumbColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return tokens.accentPrimary;
          }
          return tokens.textTertiary;
        }),
        trackColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return tokens.accentPrimarySubtle;
          }
          return tokens.bgSurfaceAlt;
        }),
      ),

      // ── Checkbox ────────────────────────────────
      checkboxTheme: CheckboxThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return tokens.accentPrimary;
          }
          return Colors.transparent;
        }),
        checkColor: WidgetStatePropertyAll(tokens.textOnAccent),
        side: BorderSide(color: tokens.borderSubtle),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(4)),
        ),
      ),

      // ── Radio ───────────────────────────────────
      radioTheme: RadioThemeData(
        fillColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.selected)) {
            return tokens.accentPrimary;
          }
          return tokens.textTertiary;
        }),
      ),

      // ── Slider ──────────────────────────────────
      sliderTheme: SliderThemeData(
        activeTrackColor: tokens.accentPrimary,
        inactiveTrackColor: tokens.bgSurfaceAlt,
        thumbColor: tokens.accentPrimary,
        overlayColor: tokens.accentPrimarySubtle,
        valueIndicatorColor: tokens.accentPrimary,
        valueIndicatorTextStyle: GoogleFonts.plusJakartaSans(
          color: tokens.textOnAccent,
          fontSize: 12,
        ),
      ),

      // ── Badge ───────────────────────────────────
      badgeTheme: BadgeThemeData(
        backgroundColor: tokens.accentCoral,
        textColor: tokens.textOnAccent,
        textStyle: GoogleFonts.plusJakartaSans(
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
        smallSize: 8,
        largeSize: 20,
      ),

      // ── Menu bar / Menu ─────────────────────────
      menuBarTheme: MenuBarThemeData(
        style: MenuStyle(
          backgroundColor: WidgetStatePropertyAll(tokens.bgElevated),
          shape: WidgetStatePropertyAll(
            RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(tokens.radiusMd)),
            ),
          ),
        ),
      ),

    );
  }
}
