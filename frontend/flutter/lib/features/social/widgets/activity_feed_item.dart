import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../models/feed_item.dart';

class ActivityFeedItem extends StatelessWidget {
  final FeedActivityItem item;
  final VoidCallback? onTap;

  const ActivityFeedItem({
    super.key,
    required this.item,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final semanticLabel = _description;

    return MergeSemantics(
      child: Semantics(
        label: semanticLabel,
        child: InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildIcon(),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _description,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    _formattedDate,
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      color: AppColors.textMuted,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
      ),
    ),
  );
  }

  Widget _buildIcon() {
    switch (item.eventType) {
      case 'status_changed':
        return Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppColors.accentPrimary.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(18),
          ),
          child: const Icon(Icons.swap_horiz, color: AppColors.accentPrimary, size: 20),
        );
      case 'progress_updated':
        return Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppColors.accentSecondary.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(18),
          ),
          child: const Icon(Icons.trending_up, color: AppColors.accentSecondary, size: 20),
        );
      case 'score_set':
        return Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppColors.success.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(18),
          ),
          child: const Icon(Icons.star, color: AppColors.success, size: 20),
        );
      case 'added':
        return Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppColors.warning.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(18),
          ),
          child: const Icon(Icons.add_circle_outline, color: AppColors.warning, size: 20),
        );
      default:
        return Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppColors.textMuted.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(18),
          ),
          child: const Icon(Icons.notifications, color: AppColors.textMuted, size: 20),
        );
    }
  }

  String get _description {
    final buf = StringBuffer();
    switch (item.eventType) {
      case 'status_changed':
        buf.write('Status changed');
        if (item.oldStatus != null && item.newStatus != null) {
          buf.write(': ${_formatStatus(item.oldStatus!)} → ${_formatStatus(item.newStatus!)}');
        } else if (item.newStatus != null) {
          buf.write(' → ${_formatStatus(item.newStatus!)}');
        }
        break;
      case 'progress_updated':
        buf.write('Progress updated');
        if (item.newProgress != null) {
          if (item.oldProgress != null) {
            buf.write(': ${item.oldProgress} → ${item.newProgress}');
          } else {
            buf.write(' → ${item.newProgress}');
          }
        }
        break;
      case 'score_set':
        buf.write('Score set');
        if (item.newScore != null) {
          if (item.oldScore != null) {
            buf.write(': ${item.oldScore} → ${item.newScore}/10');
          } else {
            buf.write(': ${item.newScore}/10');
          }
        }
        break;
      case 'added':
        buf.write('Added to list');
        if (item.newStatus != null) {
          buf.write(' (${_formatStatus(item.newStatus!)})');
        }
        break;
      default:
        buf.write(item.eventType.replaceAll('_', ' '));
    }
    if (item.note != null && item.note!.isNotEmpty) {
      buf.write(' — "${item.note}"');
    }
    return buf.toString();
  }

  String _formatStatus(String status) {
    return status.replaceAll('_', ' ').split(' ').map((w) {
      if (w.isEmpty) return w;
      return '${w[0].toUpperCase()}${w.substring(1)}';
    }).join(' ');
  }

  String get _formattedDate {
    try {
      final dt = DateTime.parse(item.createdAt);
      final now = DateTime.now();
      final diff = now.difference(dt);
      if (diff.inMinutes < 1) return 'Just now';
      if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
      if (diff.inHours < 24) return '${diff.inHours}h ago';
      if (diff.inDays < 7) return '${diff.inDays}d ago';
      return '${dt.month}/${dt.day}/${dt.year}';
    } catch (_) {
      return item.createdAt;
    }
  }
}
