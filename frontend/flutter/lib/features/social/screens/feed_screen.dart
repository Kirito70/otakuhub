import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/widgets/app_empty_state.dart';
import '../models/feed_item.dart';
import '../providers/feed_provider.dart';
import '../widgets/activity_feed_item.dart';

class FeedScreen extends ConsumerStatefulWidget {
  const FeedScreen({super.key});

  @override
  ConsumerState<FeedScreen> createState() => _FeedScreenState();
}

class _FeedScreenState extends ConsumerState<FeedScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Activity Feed'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Group Activity'),
            Tab(text: 'My Activity'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _GroupFeedTab(),
          _MyActivityTab(),
        ],
      ),
    );
  }
}

class _GroupFeedTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final feedAsync = ref.watch(groupFeedNotifierProvider);

    return feedAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => AppEmptyState.error(
        message: 'Failed to load feed',
        onAction: () => ref.invalidate(groupFeedNotifierProvider),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return const AppEmptyState(
            icon: Icons.groups_outlined,
            message: 'No group activity yet. Join a group to see what others are watching.',
          );
        }
        return _FeedList(
          items: data.items,
          hasMore: data.items.length < data.total,
          onLoadMore: () =>
              ref.read(groupFeedNotifierProvider.notifier).loadMore(),
          onItemTap: (mediaId) => context.push('/media/$mediaId'),
        );
      },
    );
  }
}

class _MyActivityTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final myAsync = ref.watch(myActivityNotifierProvider);

    return myAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => AppEmptyState.error(
        message: 'Failed to load your activity',
        onAction: () => ref.invalidate(myActivityNotifierProvider),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return const AppEmptyState(
            icon: Icons.history_outlined,
            message: "You haven't logged any activity yet. Start tracking anime or manga!",
          );
        }
        return _FeedList(
          items: data.items,
          hasMore: data.items.length < data.total,
          onLoadMore: () =>
              ref.read(myActivityNotifierProvider.notifier).loadMore(),
          onItemTap: (mediaId) => context.push('/media/$mediaId'),
        );
      },
    );
  }
}

class _FeedList extends StatelessWidget {
  final List<FeedActivityItem> items;
  final bool hasMore;
  final VoidCallback onLoadMore;
  final void Function(String mediaId) onItemTap;

  const _FeedList({
    required this.items,
    required this.hasMore,
    required this.onLoadMore,
    required this.onItemTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListView.separated(
      itemCount: items.length + (hasMore ? 1 : 0),
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        if (index == items.length) {
          return Padding(
            padding: const EdgeInsets.all(16),
            child: Center(
              child: OutlinedButton(
                onPressed: onLoadMore,
                child: const Text('Load More'),
              ),
            ),
          );
        }
        final item = items[index];
        return ActivityFeedItem(
          item: item,
          onTap: () => onItemTap(item.mediaId),
        );
      },
    );
  }
}
