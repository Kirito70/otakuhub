import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/notifications/models/notification_models.dart';

class NotificationCard extends StatelessWidget {
  final NotificationItem notification;
  final VoidCallback? onTap;
  final VoidCallback? onMarkRead;
  final VoidCallback? onDelete;

  const NotificationCard({
    super.key,
    required this.notification,
    this.onTap,
    this.onMarkRead,
    this.onDelete,
  });

  IconData _iconForType(String type) {
    switch (type) {
      case 'new_episode':
        return Icons.play_circle_outline;
      case 'new_chapter':
        return Icons.auto_stories_outlined;
      case 'friend_activity':
        return Icons.people_outline;
      case 'recommendation':
        return Icons.recommend_outlined;
      case 'watch_party_invite':
        return Icons.party_mode_outlined;
      case 'watch_party_reminder':
        return Icons.notifications_active_outlined;
      default:
        return Icons.notifications_outlined;
    }
  }

  Color _colorForType(String type) {
    switch (type) {
      case 'new_episode':
        return AppColors.accentSecondary;
      case 'new_chapter':
        return AppColors.success;
      case 'friend_activity':
        return AppColors.accentPrimary;
      case 'recommendation':
        return AppColors.warning;
      case 'watch_party_invite':
        return const Color(0xFFF472B6);
      case 'watch_party_reminder':
        return AppColors.destructive;
      default:
        return AppColors.textSecondary;
    }
  }

  String _timeAgo(DateTime dateTime) {
    final now = DateTime.now();
    final diff = now.difference(dateTime);

    if (diff.inSeconds < 60) return 'just now';
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    if (diff.inDays < 7) return '${diff.inDays}d ago';
    return '${dateTime.month}/${dateTime.day}/${dateTime.year}';
  }

  @override
  Widget build(BuildContext context) {
    final color = _colorForType(notification.type);

    return Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.endToStart,
      background: Container(
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        color: AppColors.destructive.withValues(alpha: 0.8),
        child: const Icon(Icons.delete_outline, color: Colors.white, size: 24),
      ),
      onDismissed: (_) => onDelete?.call(),
      child: MergeSemantics(
        child: Semantics(
          label: '${notification.title}${notification.body != null ? ', ${notification.body}' : ''}'
              '${!notification.isRead ? ', unread' : ''}',
          child: InkWell(
            onTap: onTap,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              color: notification.isRead ? Colors.transparent : AppColors.accentPrimary.withValues(alpha: 0.05),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Type icon
                  Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: color.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(_iconForType(notification.type), color: color, size: 20),
                  ),
                  const SizedBox(width: 12),

                  // Content
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                notification.title,
                                style: TextStyle(
                                  fontSize: 14,
                                  fontWeight: notification.isRead ? FontWeight.w400 : FontWeight.w600,
                                  color: AppColors.textPrimary,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _timeAgo(notification.createdAt),
                              style: TextStyle(
                                fontSize: 11,
                                color: AppColors.textMuted,
                              ),
                            ),
                          ],
                        ),
                        if (notification.body != null && notification.body!.isNotEmpty)
                          Padding(
                            padding: const EdgeInsets.only(top: 2),
                            child: Text(
                              notification.body!,
                              style: TextStyle(
                                fontSize: 13,
                                color: AppColors.textSecondary,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),

                        // Read/unread indicator + mark-read button
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            if (!notification.isRead)
                              Container(
                                width: 8,
                                height: 8,
                                decoration: const BoxDecoration(
                                  color: AppColors.accentPrimary,
                                  shape: BoxShape.circle,
                                ),
                              )
                            else
                              const SizedBox(width: 8),
                            const Spacer(),
                            if (!notification.isRead && onMarkRead != null)
                              GestureDetector(
                                onTap: onMarkRead,
                                child: Text(
                                  'Mark read',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: AppColors.accentSecondary,
                                  ),
                                ),
                              ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
