import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/widgets/app_empty_state.dart';
import '../providers/recommendations_provider.dart';
import '../widgets/recommend_card.dart';

class RecommendationsScreen extends ConsumerStatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  ConsumerState<RecommendationsScreen> createState() =>
      _RecommendationsScreenState();
}

class _RecommendationsScreenState extends ConsumerState<RecommendationsScreen>
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
        title: const Text('Recommendations'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Inbox'),
            Tab(text: 'Sent'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _InboxTab(),
          _SentTab(),
        ],
      ),
    );
  }
}

class _InboxTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final inboxAsync = ref.watch(inboxNotifierProvider);

    return inboxAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => AppEmptyState.error(
        message: 'Failed to load inbox',
        onAction: () => ref.invalidate(inboxNotifierProvider),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return const AppEmptyState(
            icon: Icons.mail_outline,
            message: 'No recommendations in your inbox yet.',
          );
        }
        return ListView.builder(
          itemCount: data.items.length + (data.items.length < data.total ? 1 : 0),
          itemBuilder: (context, index) {
            if (index == data.items.length) {
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Center(
                  child: OutlinedButton(
                    onPressed: () =>
                        ref.read(inboxNotifierProvider.notifier).loadMore(),
                    child: const Text('Load More'),
                  ),
                ),
              );
            }
            final rec = data.items[index];
            return RecommendCard(
              rec: rec,
              isIncoming: true,
              onViewMedia: () => context.push('/media/${rec.mediaId}'),
              onAcknowledge: () => ref
                  .read(acknowledgeActionProvider.notifier)
                  .acknowledge(rec.id),
            );
          },
        );
      },
    );
  }
}

class _SentTab extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sentAsync = ref.watch(sentNotifierProvider);

    return sentAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => AppEmptyState.error(
        message: 'Failed to load sent recommendations',
        onAction: () => ref.invalidate(sentNotifierProvider),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return const AppEmptyState(
            icon: Icons.send_outlined,
            message: "You haven't sent any recommendations yet.",
          );
        }
        return ListView.builder(
          itemCount: data.items.length + (data.items.length < data.total ? 1 : 0),
          itemBuilder: (context, index) {
            if (index == data.items.length) {
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Center(
                  child: OutlinedButton(
                    onPressed: () =>
                        ref.read(sentNotifierProvider.notifier).loadMore(),
                    child: const Text('Load More'),
                  ),
                ),
              );
            }
            final rec = data.items[index];
            return RecommendCard(
              rec: rec,
              isIncoming: false,
              onViewMedia: () => context.push('/media/${rec.mediaId}'),
            );
          },
        );
      },
    );
  }
}
