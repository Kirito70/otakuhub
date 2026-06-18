import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/notifications/models/notification_models.dart';
import 'package:otakuhub/features/notifications/providers/notification_providers.dart';
import 'package:otakuhub/features/notifications/widgets/notification_card.dart';

class NotificationsScreen extends ConsumerStatefulWidget {
  final int initialTabIndex;

  const NotificationsScreen({super.key, this.initialTabIndex = 0});

  @override
  ConsumerState<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends ConsumerState<NotificationsScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: 2,
      vsync: this,
      initialIndex: widget.initialTabIndex,
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _handleMarkAllRead() async {
    try {
      await ref.read(markReadNotifierProvider.notifier).markAllAsRead();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('All notifications marked as read')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to mark all as read: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        actions: [
          IconButton(
            icon: const Icon(Icons.done_all_outlined),
            tooltip: 'Mark all as read',
            onPressed: _handleMarkAllRead,
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'All'),
            Tab(text: 'Unread'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _AllTab(),
          _UnreadTab(),
        ],
      ),
    );
  }
}

// --- All Tab ---

class _AllTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncNotifs = ref.watch(allNotificationsNotifierProvider);

    return asyncNotifs.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline,
                  color: AppColors.destructive, size: 48),
              const SizedBox(height: 12),
              Text(
                'Failed to load notifications',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () =>
                    ref.invalidate(allNotificationsNotifierProvider),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.notifications_off_outlined,
                    size: 64, color: AppColors.textMuted),
                const SizedBox(height: 16),
                Text(
                  'No notifications yet',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'We\'ll let you know when something happens',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              ],
            ),
          );
        }
        return _NotificationList(
          items: data.items,
          total: data.total,
          isUnreadTab: false,
        );
      },
    );
  }
}

// --- Unread Tab ---

class _UnreadTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncNotifs = ref.watch(unreadNotificationsNotifierProvider);

    return asyncNotifs.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline,
                  color: AppColors.destructive, size: 48),
              const SizedBox(height: 12),
              Text(
                'Failed to load unread notifications',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () =>
                    ref.invalidate(unreadNotificationsNotifierProvider),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.mark_email_read_outlined,
                    size: 64, color: AppColors.textMuted),
                const SizedBox(height: 16),
                Text(
                  'All caught up!',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'No unread notifications',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              ],
            ),
          );
        }
        return _NotificationList(
          items: data.items,
          total: data.total,
          isUnreadTab: true,
        );
      },
    );
  }
}

// --- Shared notification list ---

class _NotificationList extends ConsumerWidget {
  final List<NotificationItem> items;
  final int total;
  final bool isUnreadTab;

  const _NotificationList({
    required this.items,
    required this.total,
    required this.isUnreadTab,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return RefreshIndicator(
      onRefresh: () async {
        if (isUnreadTab) {
          ref.invalidate(unreadNotificationsNotifierProvider);
        } else {
          ref.invalidate(allNotificationsNotifierProvider);
        }
      },
      child: NotificationListener<ScrollNotification>(
        onNotification: (scrollInfo) {
          if (scrollInfo is ScrollEndNotification &&
              scrollInfo.metrics.pixels >= scrollInfo.metrics.maxScrollExtent - 100) {
            if (isUnreadTab) {
              ref.read(unreadNotificationsNotifierProvider.notifier).loadMore();
            } else {
              ref.read(allNotificationsNotifierProvider.notifier).loadMore();
            }
          }
          return false;
        },
        child: ListView.separated(
          padding: const EdgeInsets.symmetric(vertical: 4),
          itemCount: items.length + (items.length < total ? 1 : 0),
          separatorBuilder: (_, __) => Divider(
            height: 1,
            color: AppColors.borderDefault.withValues(alpha: 0.5),
            indent: 68,
          ),
          itemBuilder: (context, index) {
            if (index >= items.length) {
              return const Padding(
                padding: EdgeInsets.all(16),
                child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
              );
            }
            final notif = items[index];
            return NotificationCard(
              notification: notif,
              onTap: notif.isRead
                  ? null
                  : () {
                      ref.read(markReadNotifierProvider.notifier).markAsRead(notif.id);
                    },
              onMarkRead: () {
                ref.read(markReadNotifierProvider.notifier).markAsRead(notif.id);
              },
              onDelete: () {
                ref.read(deleteNotificationNotifierProvider.notifier).delete(notif.id);
              },
            );
          },
        ),
      ),
    );
  }
}
