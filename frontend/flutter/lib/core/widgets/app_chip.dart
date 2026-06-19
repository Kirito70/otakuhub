import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — AppChip: filter/tag chip with optional leading dot and x-close.
///
/// Selected state: accentPrimary bg with textOnAccent text.
/// Unselected: bgSurfaceAlt with borderSubtle border.
/// Can show x-close button (onRemove provided).
class AppChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback? onTap;
  final VoidCallback? onRemove;
  final Color? dotColor;

  const AppChip({
    super.key,
    required this.label,
    this.isSelected = false,
    this.onTap,
    this.onRemove,
    this.dotColor,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: EdgeInsets.only(
          left: 12,
          right: onRemove != null ? 6 : 12,
          top: 6,
          bottom: 6,
        ),
        decoration: BoxDecoration(
          color: isSelected ? tokens.accentPrimary : tokens.bgSurfaceAlt,
          borderRadius: BorderRadius.circular(tokens.radiusPill),
          border: Border.all(
            color: isSelected ? Colors.transparent : tokens.borderSubtle,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (dotColor != null) ...[
              Container(
                width: 6,
                height: 6,
                decoration: BoxDecoration(
                  color: dotColor,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
            ],
            Text(
              label,
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: isSelected ? tokens.textOnAccent : tokens.textPrimary,
                height: 1.2,
              ),
            ),
            if (onRemove != null) ...[
              const SizedBox(width: 4),
              GestureDetector(
                onTap: onRemove,
                child: Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isSelected
                        ? Colors.white.withValues(alpha: 0.2)
                        : tokens.borderSubtle,
                  ),
                  child: Icon(
                    Icons.close_rounded,
                    size: 14,
                    color: isSelected
                        ? tokens.textOnAccent
                        : tokens.textTertiary,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
