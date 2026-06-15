import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/tracking/models/list_entry.dart';
import 'package:otakuhub/features/tracking/providers/tracking_providers.dart';
import 'package:otakuhub/features/tracking/widgets/progress_widget.dart';
import 'package:otakuhub/features/tracking/widgets/score_widget.dart';

class MyListScreen extends ConsumerStatefulWidget {
  const MyListScreen({super.key});

  @override
  ConsumerState<MyListScreen> createState() => _MyListScreenState();
}

class _MyListScreenState extends ConsumerState<MyListScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  static const _statusTabs = [
    'watching',
    'reading',
    'completed',
    'paused',
    'dropped',
    'plan',
  ];

  static const _tabLabels = [
    'Watching',
    'Reading',
    'Completed',
    'Paused',
    'Dropped',
    'Plan',
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: _statusTabs.length, vsync: this);
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
        title: const Text('My List'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(invalidateListDataProvider),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          isScrollable: true,
          indicatorColor: AppColors.accentPrimary,
          labelColor: AppColors.accentPrimary,
          unselectedLabelColor: AppColors.textSecondary,
          tabs: _tabLabels.map((l) => Tab(text: l)).toList(),
        ),
      ),
      body: Column(
        children: [
          // Stats bar
          _StatsBar(),
          // Tab content
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: _statusTabs.map((status) {
                return _ListTab(status: status);
              }).toList(),
            ),
          ),
        ],
      ),
      bottomNavigationBar: _HistorySection(),
    );
  }
}

// --- Stats bar ---
class _StatsBar extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final statsAsync = ref.watch(listStatsProvider);
    return statsAsync.when(
      loading: () => const SizedBox(height: 40),
      error: (_, __) => const SizedBox(height: 40),
      data: (stats) {
        final chips = _buildChips(stats);
        if (chips.isEmpty) return const SizedBox(height: 40);
        return Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 8),
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: chips.length,
            separatorBuilder: (_, __) => const SizedBox(width: 6),
            itemBuilder: (_, i) => chips[i],
          ),
        );
      },
    );
  }

  List<Widget> _buildChips(ListStats stats) {
    final map = <String, int>{
      'Total': stats.total,
      'Watching': stats.watching,
      'Reading': stats.reading,
      'Completed': stats.completed,
      'Paused': stats.paused,
      'Dropped': stats.dropped,
      'Plan': stats.planToWatch + stats.planToRead,
    };
    return map.entries
        .where((e) => e.value > 0)
        .map((e) => Chip(
              label: Text('${e.key}: ${e.value}'),
              labelStyle: const TextStyle(fontSize: 11),
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              visualDensity: VisualDensity.compact,
              backgroundColor: AppColors.bgElevated,
              side: BorderSide.none,
              padding: EdgeInsets.zero,
            ))
        .toList();
  }
}

// --- List tab ---
class _ListTab extends ConsumerWidget {
  final String status;

  const _ListTab({required this.status});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final entriesAsync = ref.watch(listEntriesProvider(status));

    return entriesAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: AppColors.destructive),
            const SizedBox(height: 8),
            const Text('Failed to load entries',
                style: TextStyle(color: AppColors.textSecondary)),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () => ref.invalidate(listEntriesProvider(status)),
              child: const Text('Retry'),
            ),
          ],
        ),
      ),
      data: (entries) {
        if (entries.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.playlist_remove, size: 48, color: AppColors.textMuted),
                const SizedBox(height: 8),
                Text(
                  'No ${status.replaceAll('_', ' ')} entries',
                  style: const TextStyle(color: AppColors.textSecondary),
                ),
              ],
            ),
          );
        }
        return ListView.separated(
          padding: const EdgeInsets.all(8),
          itemCount: entries.length,
          separatorBuilder: (_, __) => const Divider(height: 1, color: AppColors.borderDefault),
          itemBuilder: (_, index) => _ListEntryTile(entry: entries[index]),
        );
      },
    );
  }
}

// --- List entry tile ---
class _ListEntryTile extends ConsumerWidget {
  final ListEntry entry;

  const _ListEntryTile({required this.entry});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Cover thumbnail
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: SizedBox(
              width: 52,
              height: 72,
              child: entry.coverImage != null
                  ? Image.network(
                      entry.coverImage!,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => _coverPlaceholder(),
                      loadingBuilder: (_, child, progress) {
                        if (progress == null) return child;
                        return _coverPlaceholder();
                      },
                    )
                  : _coverPlaceholder(),
            ),
          ),
          const SizedBox(width: 12),
          // Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Title
                GestureDetector(
                  onTap: () => context.goNamed(
                    RouteNames.mediaDetail,
                    pathParameters: {'id': entry.mediaId},
                  ),
                  child: Text(
                    entry.displayTitle,
                    style: const TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(height: 6),
                // Progress
                Row(
                  children: [
                    Text('Progress: ',
                        style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                    ProgressWidget(
                      value: entry.progress,
                      max: entry.episodeCount ?? entry.chapterCount,
                      onChange: (newProgress) {
                        ref.read(updateProgressProvider(
                          (mediaId: entry.mediaId, progress: newProgress),
                        ));
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                // Score
                Row(
                  children: [
                    Text('Score: ',
                        style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                    ScoreWidget(
                      value: entry.score,
                      onChange: (newScore) {
                        ref.read(updateScoreProvider(
                          (mediaId: entry.mediaId, score: newScore),
                        ));
                      },
                    ),
                  ],
                ),
                // Status badge
                if (entry.repeatCount > 0)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      'Rewatch #${entry.repeatCount}',
                      style: const TextStyle(color: AppColors.accentSecondary, fontSize: 11),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _coverPlaceholder() {
    return Container(
      color: AppColors.bgElevated,
      child: const Center(
        child: Icon(Icons.movie_outlined, color: AppColors.textMuted, size: 20),
      ),
    );
  }
}

// --- History bottom section ---
class _HistorySection extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(listHistoryProvider);
    return historyAsync.when(
      loading: () => const SizedBox(height: 40),
      error: (_, __) => const SizedBox.shrink(),
      data: (items) {
        if (items.isEmpty) return const SizedBox.shrink();
        return Container(
          height: 200,
          decoration: BoxDecoration(
            color: AppColors.bgSecondary,
            border: Border(top: BorderSide(color: AppColors.borderDefault)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
                child: Text('Recent Activity',
                    style: TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 13,
                        fontWeight: FontWeight.bold)),
              ),
              Expanded(
                child: ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  itemCount: items.length > 10 ? 10 : items.length,
                  separatorBuilder: (_, __) =>
                      const Divider(height: 1, color: AppColors.borderDefault),
                  itemBuilder: (_, i) {
                    final item = items[i];
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          Expanded(
                            child: Text(
                              item.eventDescription,
                              style: const TextStyle(
                                  color: AppColors.textSecondary, fontSize: 12),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          Text(
                            _relativeDate(item.createdAt),
                            style: const TextStyle(
                                color: AppColors.textMuted, fontSize: 11),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  String _relativeDate(String dateStr) {
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final diff = now.difference(date);
      if (diff.inMinutes < 1) return 'Just now';
      if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
      if (diff.inHours < 24) return '${diff.inHours}h ago';
      if (diff.inDays < 7) return '${diff.inDays}d ago';
      return '${date.month}/${date.day}';
    } catch (_) {
      return '';
    }
  }
}
