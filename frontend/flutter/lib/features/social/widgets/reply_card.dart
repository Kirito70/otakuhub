import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../models/discussion.dart';

class ReplyCard extends StatelessWidget {
  final DiscussionReply reply;
  final bool isRevealed;
  final VoidCallback? onRevealSpoiler;

  const ReplyCard({
    super.key,
    required this.reply,
    this.isRevealed = false,
    this.onRevealSpoiler,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'User #${reply.userId.length >= 8 ? reply.userId.substring(0, 8) : reply.userId}',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: AppColors.textMuted,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                _formattedDate(reply.createdAt),
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: AppColors.textMuted,
                ),
              ),
              if (reply.hasSpoilers) ...[
                const SizedBox(width: 8),
                Container(
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
            ],
          ),
          const SizedBox(height: 6),
          if (reply.hasSpoilers && !isRevealed)
            TextButton.icon(
              onPressed: onRevealSpoiler,
              icon: const Icon(Icons.warning_amber, size: 16, color: AppColors.warning),
              label: const Text(
                'Show Spoiler',
                style: TextStyle(color: AppColors.warning),
              ),
            )
          else
            Text(
              reply.body,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          const Divider(height: 24),
        ],
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
