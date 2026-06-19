import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — SectionHeader: a section header with title, optional "See all" action,
/// and optional leading accent bar.
class SectionHeader extends StatelessWidget {
  final String title;
  final String? seeAllLabel;
  final VoidCallback? onSeeAll;
  final bool showAccentBar;

  const SectionHeader({
    super.key,
    required this.title,
    this.seeAllLabel,
    this.onSeeAll,
    this.showAccentBar = false,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Padding(
      padding: EdgeInsets.only(
        left: tokens.spaceMd,
        right: tokens.spaceMd,
        bottom: tokens.spaceSm,
      ),
      child: Row(
        children: [
          if (showAccentBar) ...[
            Container(
              width: 3,
              height: 18,
              decoration: BoxDecoration(
                color: tokens.accentPrimary,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(width: 8),
          ],
          Text(
            title,
            style: TextStyle(
              fontFamily: 'Plus Jakarta Sans',
              fontSize: 20,
              fontWeight: FontWeight.w600,
              height: 26 / 20,
              color: tokens.textPrimary,
            ),
          ),
          const Spacer(),
          if (seeAllLabel != null && onSeeAll != null)
            GestureDetector(
              onTap: onSeeAll,
              child: Padding(
                padding: const EdgeInsets.only(left: 8),
                child: Text(
                  seeAllLabel!,
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: tokens.accentPrimary,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
