import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — AppEmptyState: centered empty/error state with optional retry button.
///
/// Two constructors:
/// - `AppEmptyState(...)` — generic empty state
/// - `AppEmptyState.error(...)` — error state with retry
class AppEmptyState extends StatelessWidget {
  final IconData icon;
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  const AppEmptyState({
    super.key,
    this.icon = Icons.inbox_outlined,
    this.message = 'Nothing here yet',
    this.actionLabel,
    this.onAction,
  });

  const AppEmptyState.error({
    super.key,
    this.icon = Icons.error_outline_rounded,
    this.message = 'Something went wrong',
    this.actionLabel = 'Retry',
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Center(
      child: Padding(
        padding: EdgeInsets.all(tokens.spaceLg),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: tokens.bgSurfaceAlt,
                borderRadius: BorderRadius.circular(tokens.radiusXl),
              ),
              child: Icon(
                icon,
                size: 36,
                color: tokens.textTertiary,
              ),
            ),
            SizedBox(height: tokens.spaceMd),
            Text(
              message,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: 16,
                fontWeight: FontWeight.w500,
                color: tokens.textSecondary,
                height: 1.4,
              ),
            ),
            if (actionLabel != null && onAction != null) ...[
              SizedBox(height: tokens.spaceMd),
              OutlinedButton.icon(
                onPressed: onAction,
                icon: Icon(Icons.refresh_rounded, size: 16),
                label: Text(actionLabel!),
                style: OutlinedButton.styleFrom(
                  foregroundColor: tokens.accentPrimary,
                  side: BorderSide(color: tokens.borderSubtle),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(tokens.radiusMd),
                  ),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 12,
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
