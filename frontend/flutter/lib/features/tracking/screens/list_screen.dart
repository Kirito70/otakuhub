import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';
import 'package:otakuhub/core/widgets/app_empty_state.dart';
import 'package:otakuhub/core/widgets/focusable_widget.dart';
import 'package:otakuhub/core/widgets/poster_card.dart';
import 'package:otakuhub/core/widgets/score_chip.dart';
import 'package:otakuhub/core/widgets/section_header.dart';
import 'package:otakuhub/core/widgets/skeletons.dart';
import 'package:otakuhub/core/widgets/status_pill.dart';
import 'package:otakuhub/features/tracking/models/list_entry.dart';
import 'package:otakuhub/features/tracking/models/list_page_data.dart';
import 'package:otakuhub/features/tracking/providers/filter_provider.dart';
import 'package:otakuhub/features/tracking/providers/list_providers.dart';
import 'package:otakuhub/features/tracking/widgets/filter_bar.dart';

/// ADR 094 Section 6.4 — Unified List Page.
///
/// Three sub-tabs: Your List · Discover · Calendar.
/// Shared filter bar (Section 6.4.1) pinned below the tab bar.
/// Uses DefaultTabController + Scaffold with column layout instead of
/// NestedScrollView because TabBarView + NestedScrollView + CustomScrollView
/// triggers a null paint error in Flutter's test framework.
class ListScreen extends ConsumerStatefulWidget {
  final ListPageTab? initialTab;

  const ListScreen({super.key, this.initialTab});

  @override
  ConsumerState<ListScreen> createState() => _ListScreenState();
}

class _ListScreenState extends ConsumerState<ListScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  static const _tabKeys = [
    ListPageTab.yourList,
    ListPageTab.discover,
    ListPageTab.calendar,
  ];

  @override
  void initState() {
    super.initState();
    final initialIndex = widget.initialTab != null
        ? _tabKeys.indexOf(widget.initialTab!)
        : 0;
    _tabController = TabController(
      length: _tabKeys.length,
      vsync: this,
      initialIndex: initialIndex < 0 ? 0 : initialIndex,
    );
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        final tab = _tabKeys[_tabController.index];
        ref.read(filterSortByTabProvider(tab));
        setState(() {}); // rebuild filter bar with new tab context
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 600;

    return Scaffold(
      body: Column(
        children: [
          // --- App bar ---
          Material(
            color: tokens.bgBase,
            child: SafeArea(
              bottom: false,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Padding(
                    padding: EdgeInsets.symmetric(
                      horizontal: tokens.spaceMd,
                      vertical: tokens.spaceSm,
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            'My Library',
                            style: TextStyle(
                              fontFamily: 'Plus Jakarta Sans',
                              fontSize: isCompact ? 22 : 28,
                              fontWeight: FontWeight.w700,
                              color: tokens.textPrimary,
                            ),
                          ),
                        ),
                        IconButton(
                          icon: Icon(Icons.search_rounded, color: tokens.textSecondary),
                          onPressed: () => context.push('/search'),
                          tooltip: 'Search',
                        ),
                      ],
                    ),
                  ),
                  // --- Sub-tabs ---
                  TabBar(
                    controller: _tabController,
                    isScrollable: true,
                    indicatorColor: tokens.accentPrimary,
                    indicatorWeight: 2,
                    labelColor: tokens.accentPrimary,
                    unselectedLabelColor: tokens.textTertiary,
                    labelStyle: TextStyle(
                      fontFamily: 'Plus Jakarta Sans',
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                    unselectedLabelStyle: TextStyle(
                      fontFamily: 'Plus Jakarta Sans',
                      fontSize: 15,
                      fontWeight: FontWeight.w500,
                    ),
                    tabs: const [
                      Tab(text: 'Your List'),
                      Tab(text: 'Discover'),
                      Tab(text: 'Calendar'),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // --- Sticky filter bar ---
          Material(
            color: tokens.bgBase,
            child: ListFilterBar(
              currentTab: _tabKeys[_tabController.index],
            ),
          ),

          // --- Tab content ---
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _YourListTab(key: const ValueKey('your_list')),
                _DiscoverTab(key: const ValueKey('discover')),
                _CalendarTab(key: const ValueKey('calendar')),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Your List sub-tab
// ---------------------------------------------------------------------------
class _YourListTab extends ConsumerWidget {
  const _YourListTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tokens = context.tokens;
    final entriesAsync = ref.watch(yourListProvider);
    final statsAsync = ref.watch(yourListStatsProvider);
    final screenWidth = MediaQuery.of(context).size.width;
    final crossAxisCount = screenWidth < 600 ? 2 : (screenWidth < 1024 ? 3 : 4);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(yourListProvider);
        ref.invalidate(yourListStatsProvider);
      },
      child: CustomScrollView(
        slivers: [
          // --- Stats header ---
          SliverToBoxAdapter(
            child: statsAsync.when(
              loading: () => const SizedBox(height: 36),
              error: (_, __) => const SizedBox(height: 36),
              data: (stats) => _StatsBar(stats: stats),
            ),
          ),

          // --- Content ---
          entriesAsync.when(
            loading: () => SliverToBoxAdapter(
              child: _buildSkeletons(tokens, crossAxisCount),
            ),
            error: (err, _) => SliverToBoxAdapter(
              child: AppEmptyState(
                icon: Icons.error_outline_rounded,
                message: 'Failed to load your list',
                actionLabel: 'Retry',
                onAction: () => ref.invalidate(yourListProvider),
              ),
            ),
            data: (entries) {
              if (entries.isEmpty) {
                return SliverToBoxAdapter(
                  child: _buildEmptyYourList(tokens),
                );
              }
              return SliverToBoxAdapter(
                child: Padding(
                  padding: EdgeInsets.all(tokens.spaceMd),
                  child: GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: crossAxisCount,
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                      childAspectRatio: 0.7,
                    ),
                    itemCount: entries.length,
                    itemBuilder: (_, index) => FocusableWidget(
                      child: _ListEntryCard(entry: entries[index]),
                    ),
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyYourList(AppTokens tokens) {
    return Padding(
      padding: EdgeInsets.all(tokens.spaceXl),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          AppEmptyState(
            icon: Icons.playlist_add_rounded,
            message: 'Start building your list\nTrack what you\'re watching and reading',
            actionLabel: 'Discover titles',
          ),
        ],
      ),
    );
  }

  Widget _buildSkeletons(AppTokens tokens, int crossAxisCount) {
    return Padding(
      padding: EdgeInsets.all(tokens.spaceMd),
      child: GridView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: crossAxisCount,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 0.7,
        ),
        itemCount: crossAxisCount * 3,
        itemBuilder: (_, __) => Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 160,
              decoration: BoxDecoration(
                color: const Color(0xFF1A1A1A),
                borderRadius: BorderRadius.circular(14),
              ),
              child: const Center(
                child: Icon(Icons.movie_outlined, size: 24, color: Color(0xFF6B7280)),
              ),
            ),
            const SizedBox(height: 6),
            AppSkeleton.textLine(width: double.infinity, height: 12),
            const SizedBox(height: 4),
            AppSkeleton.textLine(width: 60, height: 10),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Stats bar
// ---------------------------------------------------------------------------
class _StatsBar extends StatelessWidget {
  final ListStats stats;

  const _StatsBar({required this.stats});

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    final statItems = [
      ('Watching', stats.watching + stats.reading),
      ('Completed', stats.completed),
      ('Scored', stats.total > 0 ? '${(stats.completed / (stats.total > 0 ? stats.total : 1) * 10).toStringAsFixed(1)}' : '—'),
    ];

    return Container(
      height: 44,
      padding: EdgeInsets.symmetric(horizontal: tokens.spaceMd),
      child: Row(
        children: statItems.map((item) {
          return Padding(
            padding: const EdgeInsets.only(right: 20),
            child: Row(
              children: [
                Text(
                  '${item.$2}',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                    color: tokens.textPrimary,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  item.$1,
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 13,
                    color: tokens.textTertiary,
                  ),
                ),
              ],
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// List entry card (PosterCard with entry data overlay)
// ---------------------------------------------------------------------------
class _ListEntryCard extends ConsumerWidget {
  final ListEntry entry;

  const _ListEntryCard({required this.entry});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tokens = context.tokens;

    final semanticLabel = '${entry.displayTitle}, '
        '${_statusToDisplay(entry.status)}, '
        '${entry.progress}/${entry.episodeCount ?? entry.chapterCount ?? '?'}';

    return MergeSemantics(
      child: Semantics(
        label: semanticLabel,
        child: GestureDetector(
          onTap: () => context.goNamed(
        RouteNames.mediaDetail,
        pathParameters: {'id': entry.mediaId},
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Poster
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(tokens.radiusMd),
              child: Stack(
                fit: StackFit.expand,
                children: [
                  if (entry.coverImage != null)
                    CachedNetworkImage(
                      imageUrl: entry.coverImage!,
                      fit: BoxFit.cover,
                      errorWidget: (_, __, ___) => _posterPlaceholder(tokens),
                    )
                  else
                    _posterPlaceholder(tokens),
                  // Status badge
                  Positioned(
                    top: 6,
                    left: 6,
                    child: StatusPill(
                      status: _statusToDisplay(entry.status),
                      fontSize: 9,
                    ),
                  ),
                  // Score
                  if (entry.score != null)
                    Positioned(
                      top: 6,
                      right: 6,
                      child: ScoreChip(
                        score: entry.score!,
                        size: 28,
                        compact: true,
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 6),
          // Title
          Text(
            entry.displayTitle,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: TextStyle(
              fontFamily: 'Plus Jakarta Sans',
              fontSize: 13,
              fontWeight: FontWeight.w500,
              color: tokens.textPrimary,
            ),
          ),
          // Progress
          Text(
            '${entry.progress}/${entry.episodeCount ?? entry.chapterCount ?? '?'}',
            style: TextStyle(
              fontFamily: 'Plus Jakarta Sans',
              fontSize: 11,
              color: tokens.textTertiary,
            ),
          ),
        ],
      ),
    ),
    ),
  );
  }

  Widget _posterPlaceholder(AppTokens tokens) {
    return Container(
      color: tokens.bgSurfaceAlt,
      child: Center(
        child: Icon(Icons.movie_outlined, size: 28, color: tokens.textTertiary),
      ),
    );
  }

  String _statusToDisplay(String status) {
    switch (status) {
      case 'watching':
        return 'Watching';
      case 'reading':
        return 'Reading';
      case 'completed':
        return 'Completed';
      case 'paused':
        return 'Paused';
      case 'dropped':
        return 'Dropped';
      case 'plan_to_watch':
        return 'Plan';
      case 'plan_to_read':
        return 'Plan';
      default:
        return status;
    }
  }
}

// ---------------------------------------------------------------------------
// Discover sub-tab
// ---------------------------------------------------------------------------
class _DiscoverTab extends ConsumerWidget {
  const _DiscoverTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tokens = context.tokens;
    final showRails = ref.watch(discoverShowRailsProvider);
    final screenWidth = MediaQuery.of(context).size.width;
    final crossAxisCount = screenWidth < 600 ? 2 : (screenWidth < 1024 ? 3 : 4);

    if (showRails) {
      return _buildDiscoverWithRails(tokens, ref, screenWidth);
    }

    // Filtered grid
    final browseAsync = ref.watch(discoverProvider);
    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(discoverProvider),
      child: browseAsync.when(
        loading: () => SingleChildScrollView(
          padding: EdgeInsets.all(tokens.spaceMd),
          child: GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 0.7,
            ),
            itemCount: crossAxisCount * 3,
            itemBuilder: (_, index) => Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  height: 160,
                  decoration: BoxDecoration(
                    color: const Color(0xFF1A1A1A),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Center(
                    child: Icon(Icons.movie_outlined, size: 24, color: Color(0xFF6B7280)),
                  ),
                ),
                const SizedBox(height: 6),
                AppSkeleton.textLine(width: double.infinity, height: 12),
              ],
            ),
          ),
        ),
        error: (err, _) => Center(
          child: AppEmptyState(
            icon: Icons.error_outline_rounded,
            message: 'Failed to load',
            actionLabel: 'Retry',
            onAction: () => ref.invalidate(discoverProvider),
          ),
        ),
        data: (response) {
          if (response.items.isEmpty) {
            return Center(
              child: AppEmptyState(
                icon: Icons.search_off_rounded,
                message: 'No titles match your filters\nTry adjusting or resetting filters',
                actionLabel: 'Reset filters',
                onAction: () => ref.read(filterStateProvider.notifier).state =
                    const FilterState(),
              ),
            );
          }
          return SingleChildScrollView(
            child: Column(
              children: [
                Padding(
                  padding: EdgeInsets.all(tokens.spaceMd),
                  child: GridView.builder(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: crossAxisCount,
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                      childAspectRatio: 0.7,
                    ),
                    itemCount: response.items.length,
                    itemBuilder: (_, index) => FocusableWidget(
                      child: _BrowseCard(item: response.items[index]),
                    ),
                  ),
                ),
                if (response.nextCursor != null)
                  Padding(
                    padding: EdgeInsets.all(tokens.spaceMd),
                    child: Center(
                      child: TextButton(
                        onPressed: () {
                          ref.read(filterStateProvider.notifier).state =
                              ref.read(filterStateProvider).copyWith(
                            cursor: response.nextCursor,
                          );
                        },
                        child: const Text('Load more'),
                      ),
                    ),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildDiscoverWithRails(AppTokens tokens, WidgetRef ref, double screenWidth) {
    final railsAsync = ref.watch(curatedRailsProvider);

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(curatedRailsProvider);
        ref.invalidate(discoverProvider);
      },
      child: railsAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => AppEmptyState(
          icon: Icons.error_outline_rounded,
          message: 'Failed to load',
          actionLabel: 'Retry',
          onAction: () => ref.invalidate(curatedRailsProvider),
        ),
        data: (rails) {
          if (rails.rails.isEmpty) {
            return AppEmptyState(
              icon: Icons.explore_rounded,
              message: 'Discover titles\nUse filters to find something new',
            );
          }
          return CustomScrollView(
            slivers: [
              for (final rail in rails.rails)
                SliverToBoxAdapter(
                  child: Padding(
                    padding: EdgeInsets.only(bottom: tokens.spaceLg),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        SectionHeader(title: rail.title),
                        SizedBox(
                          height: 240,
                          child: ListView.separated(
                            scrollDirection: Axis.horizontal,
                            padding: EdgeInsets.symmetric(horizontal: tokens.spaceMd),
                            itemCount: rail.items.length,
                            separatorBuilder: (_, __) => const SizedBox(width: 10),
                            itemBuilder: (ctx, i) {
                              final item = rail.items[i];
                              return FocusableWidget(
                                semanticLabel: 'Media: ${item.displayTitle}',
                                child: SizedBox(
                                  width: 140,
                                  child: PosterCard(
                                    imageUrl: item.coverImage ?? '',
                                    title: item.displayTitle,
                                    score: item.averageScore,
                                    format: item.format,
                                    onTap: () => ctx.goNamed(
                                      RouteNames.mediaDetail,
                                      pathParameters: {'id': item.id},
                                    ),
                                    width: 140,
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          );
        },
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Browse card (for Discover filtered grid)
// ---------------------------------------------------------------------------
class _BrowseCard extends ConsumerWidget {
  final BrowseResultItem item;

  const _BrowseCard({required this.item});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return PosterCard(
      imageUrl: item.coverImage ?? '',
      title: item.displayTitle,
      score: item.averageScore,
      format: item.format,
      width: 140,
      onTap: () => context.goNamed(
        RouteNames.mediaDetail,
        pathParameters: {'id': item.id},
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Calendar sub-tab
// ---------------------------------------------------------------------------
class _CalendarTab extends ConsumerWidget {
  const _CalendarTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tokens = context.tokens;
    final calendarAsync = ref.watch(calendarProvider);

    return RefreshIndicator(
      onRefresh: () async => ref.invalidate(calendarProvider),
      child: calendarAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => AppEmptyState(
          icon: Icons.error_outline_rounded,
          message: 'Failed to load schedule',
          actionLabel: 'Retry',
          onAction: () => ref.invalidate(calendarProvider),
        ),
        data: (events) {
          if (events.isEmpty) {
            return AppEmptyState(
              icon: Icons.calendar_month_rounded,
              message: 'No upcoming airings\nTry adjusting filters',
            );
          }

          // Group events by date
          final grouped = <String, List<CalendarEvent>>{};
          for (final event in events) {
            final key = _dateKey(event.airingAtDate);
            grouped.putIfAbsent(key, () => []).add(event);
          }

          final sortedDates = grouped.keys.toList()..sort();

          return CustomScrollView(
            slivers: [
              SliverPadding(
                padding: EdgeInsets.all(tokens.spaceMd),
                sliver: SliverList(
                  delegate: SliverChildBuilderDelegate(
                    (context, sectionIndex) {
                      final date = sortedDates[sectionIndex];
                      final dayEvents = grouped[date]!;

                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Date header
                          Padding(
                            padding: EdgeInsets.only(
                              top: sectionIndex == 0 ? 0 : tokens.spaceLg,
                              bottom: tokens.spaceSm,
                            ),
                            child: _DateHeader(dateStr: date),
                          ),
                          // Events for this date
                          ...dayEvents.map((event) => FocusableWidget(
                            child: _CalendarEventCard(event: event),
                          )),
                        ],
                      );
                    },
                    childCount: sortedDates.length,
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Calendar event card
// ---------------------------------------------------------------------------
class _CalendarEventCard extends ConsumerWidget {
  final CalendarEvent event;

  const _CalendarEventCard({required this.event});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tokens = context.tokens;

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: () => context.goNamed(
          RouteNames.mediaDetail,
          pathParameters: {'id': event.mediaId},
        ),
        borderRadius: BorderRadius.circular(tokens.radiusMd),
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: tokens.bgSurface,
            borderRadius: BorderRadius.circular(tokens.radiusMd),
            border: Border.all(color: tokens.borderSubtle),
          ),
          child: Row(
            children: [
              // Thumbnail
              ClipRRect(
                borderRadius: BorderRadius.circular(tokens.radiusSm),
                child: SizedBox(
                  width: 44,
                  height: 66,
                  child: event.coverImage != null
                      ? CachedNetworkImage(
                          imageUrl: event.coverImage!,
                          fit: BoxFit.cover,
                          errorWidget: (_, __, ___) => Container(
                            color: tokens.bgSurfaceAlt,
                            child: Icon(Icons.movie_outlined, size: 18, color: tokens.textTertiary),
                          ),
                        )
                      : Container(
                          color: tokens.bgSurfaceAlt,
                          child: Icon(Icons.movie_outlined, size: 18, color: tokens.textTertiary),
                        ),
                ),
              ),
              const SizedBox(width: 12),
              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      event.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: tokens.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        if (event.episodeNumber != null)
                          Text(
                            'Ep ${event.episodeNumber}',
                            style: TextStyle(
                              fontFamily: 'Plus Jakarta Sans',
                              fontSize: 12,
                              color: tokens.accentCoral,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        if (event.chapterNumber != null)
                          Text(
                            'Ch ${event.chapterNumber}',
                            style: TextStyle(
                              fontFamily: 'Plus Jakarta Sans',
                              fontSize: 12,
                              color: tokens.accentMint,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        const SizedBox(width: 8),
                        Text(
                          _formatTime(event.airingAtDate),
                          style: TextStyle(
                            fontFamily: 'Plus Jakarta Sans',
                            fontSize: 12,
                            color: tokens.textTertiary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              // Chevron
              Icon(Icons.chevron_right_rounded, size: 20, color: tokens.textTertiary),
            ],
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Date header
// ---------------------------------------------------------------------------
class _DateHeader extends StatelessWidget {
  final String dateStr;

  const _DateHeader({required this.dateStr});

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final date = DateTime.tryParse(dateStr);
    if (date == null) return const SizedBox.shrink();

    final now = DateTime.now();
    final isToday = date.year == now.year && date.month == now.month && date.day == now.day;
    final isTomorrow = date.year == now.year && date.month == now.month && date.day == now.day + 1;

    String label;
    if (isToday) {
      label = 'Today';
    } else if (isTomorrow) {
      label = 'Tomorrow';
    } else {
      const months = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
      ];
      label = '${months[date.month - 1]} ${date.day}, ${date.year}';
    }

    return Text(
      label,
      style: TextStyle(
        fontFamily: 'Plus Jakarta Sans',
        fontSize: 16,
        fontWeight: FontWeight.w700,
        color: isToday ? tokens.accentPrimary : tokens.textPrimary,
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
String _dateKey(DateTime dt) {
  return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')}';
}

String _formatTime(DateTime dt) {
  final hour = dt.hour > 12 ? dt.hour - 12 : (dt.hour == 0 ? 12 : dt.hour);
  final ampm = dt.hour >= 12 ? 'PM' : 'AM';
  final min = dt.minute.toString().padLeft(2, '0');
  return '$hour:$min $ampm';
}
