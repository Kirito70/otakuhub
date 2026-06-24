import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../models/recommendation.dart';

class RecommendCard extends StatelessWidget {
  final Recommendation rec;
  final bool isIncoming;
  final VoidCallback? onAcknowledge;
  final VoidCallback? onViewMedia;
  final bool isAcknowledging;

  const RecommendCard({
    super.key,
    required this.rec,
    required this.isIncoming,
    this.onAcknowledge,
    this.onViewMedia,
    this.isAcknowledging = false,
  });

  @override
  Widget build(BuildContext context) {
    final semanticLabel = isIncoming
        ? 'Recommendation: ${rec.message ?? "media item"}'
        : 'Recommendation: ${rec.message ?? "media item"}'
        '${rec.isAcknowledged ? ', acknowledged' : ''}';

    return MergeSemantics(
      child: Semantics(
        label: semanticLabel,
        child: Card(
      color: AppColors.bgSecondary,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(
          color: rec.isAcknowledged
              ? AppColors.borderDefault
              : AppColors.accentPrimary.withValues(alpha: 0.3),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isIncoming ? Icons.arrow_downward : Icons.arrow_upward,
                  size: 16,
                  color: AppColors.accentPrimary,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    isIncoming ? 'Recommended to you' : 'You recommended',
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
                if (rec.isAcknowledged)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.success.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      'Seen',
                      style: TextStyle(
                        color: AppColors.success,
                        fontSize: 11,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
              ],
            ),
            if (rec.message != null && rec.message!.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                rec.message!,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton.icon(
                  onPressed: onViewMedia,
                  icon: const Icon(Icons.open_in_new, size: 16),
                  label: const Text('View Media'),
                ),
                if (isIncoming && !rec.isAcknowledged)
                  TextButton.icon(
                    onPressed: isAcknowledging ? null : onAcknowledge,
                    icon: isAcknowledging
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.check, size: 16),
                    label: Text(isAcknowledging ? '...' : 'Mark Seen'),
                  ),
              ],
            ),
            ],
          ),
        ),
      ),
      ),
    );
  }
}
