import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — AppButton: primary/secondary/ghost with mutating variants.
///
/// - primary: accentPrimary bg → press slightly darker
/// - secondary: border + bgSurfaceAlt bg
/// - ghost: no bg, text only
/// Loading: shows small CircularProgressIndicator overlay
/// Icons: leading or trailing (default trailing for arrow)
class AppButton extends StatelessWidget {
  final String label;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final IconData? leadingIcon;
  final IconData? trailingIcon;
  final bool isLoading;
  final bool isDisabled;
  final double height;
  final double? width;
  final double fontSize;

  const AppButton({
    super.key,
    required this.label,
    this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.leadingIcon,
    this.trailingIcon,
    this.isLoading = false,
    this.isDisabled = false,
    this.height = 48,
    this.width,
    this.fontSize = 15,
  });

  bool get _disabled => isDisabled || isLoading || onPressed == null;

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    Color bgColor;
    Color textColor;
    BorderSide? borderSide;
    Color? splashColor;

    switch (variant) {
      case AppButtonVariant.primary:
        bgColor = tokens.accentPrimary;
        textColor = tokens.textOnAccent;
        splashColor = tokens.accentPrimary.withValues(alpha: 0.2);
        borderSide = null;
      case AppButtonVariant.secondary:
        bgColor = tokens.bgSurfaceAlt;
        textColor = tokens.textPrimary;
        borderSide = BorderSide(color: tokens.borderSubtle);
        splashColor = tokens.accentPrimary.withValues(alpha: 0.1);
      case AppButtonVariant.ghost:
        bgColor = Colors.transparent;
        textColor = tokens.accentPrimary;
        borderSide = null;
        splashColor = tokens.accentPrimary.withValues(alpha: 0.1);
    }

    return SizedBox(
      width: width,
      height: height,
      child: TextButton(
        onPressed: _disabled ? null : onPressed,
        style: TextButton.styleFrom(
          backgroundColor: _disabled ? bgColor.withValues(alpha: 0.5) : bgColor,
          foregroundColor: textColor,
          side: borderSide,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(tokens.radiusMd),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 20),
          splashFactory: InkRipple.splashFactory,
        ),
        child: AnimatedSwitcher(
          duration: const Duration(milliseconds: 200),
          child: isLoading
              ? SizedBox(
                  width: 22,
                  height: 22,
                  child: CircularProgressIndicator(
                    strokeWidth: 2.5,
                    color: textColor,
                  ),
                )
              : Row(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (leadingIcon != null) ...[
                      Icon(leadingIcon, size: 18),
                      const SizedBox(width: 8),
                    ],
                    Flexible(
                      child: Text(
                        label,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          fontSize: fontSize,
                          fontWeight: FontWeight.w600,
                          color: _disabled
                              ? textColor.withValues(alpha: 0.5)
                              : textColor,
                        ),
                      ),
                    ),
                    if (trailingIcon != null) ...[
                      const SizedBox(width: 8),
                      Icon(trailingIcon, size: 18),
                    ],
                  ],
                ),
        ),
      ),
    );
  }
}

enum AppButtonVariant { primary, secondary, ghost }
