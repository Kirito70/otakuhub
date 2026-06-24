import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../models/discussion.dart';

class DiscussionCard extends StatelessWidget {
  final Discussion discussion;
  final VoidCallback? onTap;

  const DiscussionCard({
    super.key,
    required this.discussion,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final semanticLabel = '${discussion.title ?? 'Discussion'}'
        '${discussion.hasSpoilers ? ', contains spoilers' : ''}'
        '${discussion.episodeNumber != null ? ', Episode ${discussion.episodeNumber}' : ''}'
        '${discussion.chapterNumber != null ? ', Chapter ${discussion.chapterNumber}' : ''}';

    return MergeSemantics(
      child: Semantics(
        label: semanticLabel,
        child: InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    discussion.title ?? 'Untitled',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                if (discussion.hasSpoilers)
                  Container(
                    margin: const EdgeInsets.only(left: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.warning.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      'Spoiler',
                      style: TextStyle(
                        color: AppColors.warning,
                        fontSize: 10,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              discussion.body,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppColors.textMuted,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 6),
            Row(
              children: [
                Text(
                  _formattedDate(discussion.createdAt),
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: AppColors.textMuted,
                  ),
                ),
                if (discussion.episodeNumber != null) ...[
                  const SizedBox(width: 8),
                  Text(
                    'Ep. ${discussion.episodeNumber}',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: AppColors.accentSecondary,
                    ),
                  ),
                ],
                if (discussion.chapterNumber != null) ...[
                  const SizedBox(width: 8),
                  Text(
                    'Ch. ${discussion.chapterNumber}',
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: AppColors.accentSecondary,
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
      ),
      ),
    );
  }

  String _formattedDate(String dateStr) {
    try {
      final dt = DateTime.parse(dateStr);
      return '${dt.month}/${dt.day}/${dt.year}';
    } catch (_) {
      return dateStr;
    }
  }
}
