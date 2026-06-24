import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/theme/animation_tokens.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';
import 'package:otakuhub/core/widgets/score_chip.dart';
import 'package:otakuhub/core/widgets/status_pill.dart';
import 'package:otakuhub/features/discover/models/search_data.dart';
import 'package:otakuhub/features/discover/providers/discover_providers.dart';
import 'package:otakuhub/features/discover/providers/search_provider.dart';

/// ADR 096 — Global Search Overlay (single search surface).
///
/// Compact (<600): full-screen modal pushed from right.
/// Expanded (>=600): slide-down panel inset at max-width 800px, centered, with dim scrim.
///
/// States:
///   - Empty query: recent searches + trending suggestions + genre chips
///   - Loading: skeleton cards
///   - Results: grouped by media type with media-specific icons
///   - No results: friendly message + reset button
class SearchOverlay extends ConsumerStatefulWidget {
  /// Optional initial query to pre-fill the search field.
  final String initialQuery;

  const SearchOverlay({super.key, this.initialQuery = ''});

  /// Shows the search overlay from any context.
  /// Adapts presentation based on screen width.
  /// If [initialQuery] is non-empty, it will be sent to the search provider.
  static Future<void> show(BuildContext context, {String initialQuery = ''}) {
    final width = MediaQuery.of(context).size.width;
    final animTokens = Theme.of(context).extension<AnimationTokens>();
    final td = animTokens?.slow ?? const Duration(milliseconds: 240);

    if (width < 600) {
      return Navigator.of(context).push<void>(
        PageRouteBuilder(
          pageBuilder: (context, animation, secondaryAnimation) =>
              SearchOverlay(initialQuery: initialQuery),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0.0, 1.0), // slide up from bottom (feels like a sheet, not navigation)
                end: Offset.zero,
              ).animate(CurvedAnimation(
                parent: animation,
                curve: Curves.easeOutCubic,
              )),
              child: child,
            );
          },
          fullscreenDialog: true,
        ),
      );
    } else {
      return showGeneralDialog(
        context: context,
        barrierDismissible: true,
        barrierLabel: 'Dismiss search',
        barrierColor: Colors.black54,
        transitionDuration: context.maybeAnimDuration(td),
        pageBuilder: (context, animation, secondaryAnimation) {
          return Align(
            alignment: Alignment.topCenter,
            child: Padding(
              padding: EdgeInsets.only(
                top: MediaQuery.of(context).padding.top + 16,
              ),
              child: SizedBox(
                width: 800,
                height: MediaQuery.of(context).size.height * 0.75,
                child: Material(
                  color: Colors.transparent,
                  child: SearchOverlay(initialQuery: initialQuery),
                ),
              ),
            ),
          );
        },
        transitionBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(
            opacity: animation,
            child: SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0.0, -0.05),
                end: Offset.zero,
              ).animate(CurvedAnimation(
                parent: animation,
                curve: Curves.easeOutCubic,
              )),
              child: child,
            ),
          );
        },
      );
    }
  }

  @override
  ConsumerState<SearchOverlay> createState() => _SearchOverlayState();
}

class _SearchOverlayState extends ConsumerState<SearchOverlay> {
  late final TextEditingController _searchController;
  final _focusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _searchController = TextEditingController(text: widget.initialQuery);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // Trigger search if there's an initial query
      if (widget.initialQuery.isNotEmpty) {
        ref.read(searchDebounceProvider).onQueryChanged(widget.initialQuery);
      }
      // Auto-focus the search field
      _focusNode.requestFocus();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _dismiss() {
    // Pop the overlay route
    final navigator = Navigator.of(context);
    if (navigator.canPop()) {
      navigator.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 600;
    final query = ref.watch(searchQueryProvider);
    final resultsAsync = ref.watch(globalSearchProvider(query));
    final isLoading = resultsAsync.isLoading && query.isNotEmpty;

    return Container(
      decoration: BoxDecoration(
        color: tokens.bgBase,
        borderRadius: isCompact
            ? BorderRadius.zero
            : BorderRadius.vertical(
                bottom: const Radius.circular(20),
              ),
      ),
      child: Column(
        children: [
          // --- Search bar ---
          _SearchBar(
            controller: _searchController,
            focusNode: _focusNode,
            onChanged: (value) {
              ref.read(searchDebounceProvider).onQueryChanged(value);
            },
            onClear: () {
              _searchController.clear();
              ref.read(searchQueryProvider.notifier).state = '';
              _focusNode.requestFocus();
            },
            onDismiss: _dismiss,
            isCompact: isCompact,
          ),

          // --- Results / Recent searches ---
          Expanded(
            child: query.isEmpty ? _buildRecent(tokens) : _buildResults(tokens, query, resultsAsync, isLoading),
          ),
        ],
      ),
    );
  }

  Widget _buildRecent(AppTokens tokens) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isCompact = screenWidth < 600;
    final trendingAsync = ref.watch(trendingProvider);

    return ListView(
      padding: EdgeInsets.all(tokens.spaceMd),
      children: [
        // --- Trending suggestions ---
        trendingAsync.when(
          loading: () => const SizedBox.shrink(),
          error: (_, __) => const SizedBox.shrink(),
          data: (trending) {
            if (trending.isEmpty) return const SizedBox.shrink();
            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.trending_up_rounded, size: 18, color: tokens.accentCoral),
                    const SizedBox(width: 8),
                    Text(
                      'Trending',
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: tokens.textPrimary,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: tokens.spaceSm),
                SizedBox(
                  height: 180,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: trending.length > 8 ? 8 : trending.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 10),
                    itemBuilder: (_, i) {
                      final item = trending[i];
                      return GestureDetector(
                        onTap: () {
                          _dismiss();
                          context.push('/media/${item.id}');
                        },
                        child: SizedBox(
                          width: 100,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(tokens.radiusSm),
                                  child: CachedNetworkImage(
                                    imageUrl: item.coverImageLarge ?? item.coverImageMedium ?? '',
                                    fit: BoxFit.cover,
                                    errorWidget: (_, __, ___) => Container(
                                      color: tokens.bgSurfaceAlt,
                                      child: Icon(Icons.movie_outlined, size: 24, color: tokens.textTertiary),
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                item.displayTitle,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                style: TextStyle(
                                  fontFamily: 'Plus Jakarta Sans',
                                  fontSize: 11,
                                  color: tokens.textSecondary,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          },
        ),

        SizedBox(height: tokens.spaceLg),

        // --- Quick genre chips ---
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.category_rounded, size: 18, color: tokens.textSecondary),
                const SizedBox(width: 8),
                Text(
                  'Browse by genre',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: tokens.textPrimary,
                  ),
                ),
              ],
            ),
            SizedBox(height: tokens.spaceSm),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                'Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy',
                'Horror', 'Romance', 'Sci-Fi', 'Slice of Life',
              ].map((genre) => Semantics(
                label: 'Browse $genre',
                child: ActionChip(
                  label: Text(genre, style: const TextStyle(fontSize: 13)),
                  onPressed: () {
                    _dismiss();
                    // Navigate to List > Discover with genre filter
                    context.goNamed(RouteNames.myList);
                  },
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  visualDensity: VisualDensity.compact,
                ),
              )).toList(),
            ),
          ],
        ),

        SizedBox(height: tokens.spaceLg),

        // --- Keyboard shortcut hint (desktop) ---
        if (!isCompact)
          Center(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: tokens.bgSurfaceAlt,
                borderRadius: BorderRadius.circular(tokens.radiusMd),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.keyboard_command_key_rounded, size: 16, color: tokens.textTertiary),
                  const SizedBox(width: 6),
                  Text(
                    'K',
                    style: TextStyle(
                      fontFamily: 'Plus Jakarta Sans',
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: tokens.textTertiary,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'to search',
                    style: TextStyle(
                      fontFamily: 'Plus Jakarta Sans',
                      fontSize: 13,
                      color: tokens.textTertiary,
                    ),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildResults(AppTokens tokens, String query, AsyncValue<SearchResults> asyncResults, bool isLoading) {
    return asyncResults.when(
      loading: () => _buildSkeletons(tokens),
      error: (error, _) => Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, size: 48, color: tokens.accentRose),
            const SizedBox(height: 12),
            Text(
              'Search failed',
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: 16,
                color: tokens.textSecondary,
              ),
            ),
            const SizedBox(height: 8),
            TextButton.icon(
              onPressed: () => ref.invalidate(globalSearchProvider(query)),
              icon: const Icon(Icons.refresh_rounded, size: 16),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
      data: (results) {
        if (results.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.search_off_rounded, size: 48, color: tokens.textTertiary),
                const SizedBox(height: 16),
                Text(
                  'No results for "$query"',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 16,
                    color: tokens.textSecondary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Try a different spelling or fewer filters',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 14,
                    color: tokens.textTertiary,
                  ),
                ),
                const SizedBox(height: 20),
                Semantics(
                  label: 'Browse all titles',
                  child: TextButton(
                    onPressed: () {
                      _dismiss();
                      context.push('/list');
                    },
                    child: const Text('Browse all titles →'),
                  ),
                ),
              ],
            ),
          );
        }

        return ListView(
          padding: EdgeInsets.only(
            left: tokens.spaceMd,
            right: tokens.spaceMd,
            bottom: tokens.spaceXl,
          ),
          children: [
            // Result count
            Semantics(
              label: '${results.totalCount} result${results.totalCount == 1 ? '' : 's'}',
              child: Padding(
                padding: EdgeInsets.only(
                  bottom: tokens.spaceSm,
                  top: tokens.spaceXs,
                ),
                child: Text(
                  '${results.totalCount} result${results.totalCount == 1 ? '' : 's'}',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 13,
                    color: tokens.textTertiary,
                  ),
                ),
              ),
            ),

            // Grouped sections
            for (final group in results.groups) ...[
              if (group.items.isNotEmpty) ...[
                _buildGroupSection(tokens, group, query),
                SizedBox(height: tokens.spaceMd),
              ],
            ],

            // "Browse all" — since we use limit=20, all results are shown inline.
            // No longer navigates to a separate search page.
          ],
        );
      },
    );
  }

  Widget _buildGroupSection(AppTokens tokens, SearchResultGroup group, String query) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        // Section header
        Padding(
          padding: EdgeInsets.only(bottom: tokens.spaceSm),
          child: Row(
            children: [
              Icon(_mediaTypeIcon(group.mediaType), size: 16, color: tokens.textSecondary),
              const SizedBox(width: 6),
              Text(
                group.displayName,
                style: TextStyle(
                  fontFamily: 'Plus Jakarta Sans',
                  fontSize: 15,
                  fontWeight: FontWeight.w600,
                  color: tokens.textPrimary,
                ),
              ),
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: tokens.bgSurfaceAlt,
                  borderRadius: BorderRadius.circular(tokens.radiusSm),
                ),
                child: Text(
                  '${group.count}',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: tokens.textTertiary,
                  ),
                ),
              ),
              const Spacer(),
            ],
          ),
        ),

        // Result items
        ...group.items.map((item) => _SearchResultRow(
              item: item,
              onTap: () {
                _dismiss();
                context.push('/media/${item.id}');
              },
            )),
      ],
    );
  }

  Widget _buildSkeletons(AppTokens tokens) {
    return ListView(
      padding: EdgeInsets.all(tokens.spaceMd),
      children: [
        // Count skeleton
        Container(
          height: 14,
          width: 80,
          decoration: BoxDecoration(
            color: tokens.bgHover,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        SizedBox(height: tokens.spaceMd),
        // 3 skeleton rows
        for (var i = 0; i < 3; i++) ...[
          _skeletonRow(tokens),
          SizedBox(height: tokens.spaceSm),
        ],
      ],
    );
  }

  Widget _skeletonRow(AppTokens tokens) {
    return Row(
      children: [
        Container(
          width: 48,
          height: 72,
          decoration: BoxDecoration(
            color: tokens.bgHover,
            borderRadius: BorderRadius.circular(tokens.radiusSm),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                height: 14,
                width: double.infinity,
                decoration: BoxDecoration(
                  color: tokens.bgHover,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              const SizedBox(height: 6),
              Container(
                height: 11,
                width: 100,
                decoration: BoxDecoration(
                  color: tokens.bgHover,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

}

// ---------------------------------------------------------------------------
// Search bar
// ---------------------------------------------------------------------------
class _SearchBar extends StatelessWidget {
  final TextEditingController controller;
  final FocusNode focusNode;
  final ValueChanged<String> onChanged;
  final VoidCallback onClear;
  final VoidCallback onDismiss;
  final bool isCompact;

  const _SearchBar({
    required this.controller,
    required this.focusNode,
    required this.onChanged,
    required this.onClear,
    required this.onDismiss,
    required this.isCompact,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Padding(
      padding: EdgeInsets.only(
        top: isCompact ? MediaQuery.of(context).padding.top + 8 : 8,
        left: tokens.spaceMd,
        right: tokens.spaceMd,
        bottom: tokens.spaceMd,
      ),
      child: Row(
        children: [
          // Back button (compact) or close (expanded)
          if (isCompact)
            Semantics(
              label: 'Close search',
              child: IconButton(
                icon: Icon(Icons.arrow_back_rounded, color: tokens.textPrimary),
                onPressed: onDismiss,
                tooltip: 'Close search',
              ),
            ),

          // Search field
          Expanded(
            child: Container(
              height: 48,
              decoration: BoxDecoration(
                color: tokens.bgSurfaceAlt,
                borderRadius: BorderRadius.circular(tokens.radiusMd),
                border: Border.all(color: tokens.borderSubtle),
              ),
              child: Row(
                children: [
                  const SizedBox(width: 14),
                  Icon(Icons.search_rounded, size: 20, color: tokens.textTertiary),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Semantics(
                      label: 'Search anime, manga, and manhwa',
                      child: TextField(
                        controller: controller,
                        focusNode: focusNode,
                        onChanged: onChanged,
                        style: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          fontSize: 16,
                          color: tokens.textPrimary,
                        ),
                        decoration: InputDecoration(
                          hintText: isCompact ? 'Search…' : 'Search anime, manga, manhwa…',
                        hintStyle: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          fontSize: 16,
                          color: tokens.textTertiary,
                        ),
                        border: InputBorder.none,
                        isDense: true,
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                  ),
                ),
                // Clear button
                if (controller.text.isNotEmpty)
                    Semantics(
                      label: 'Clear search',
                      child: IconButton(
                        icon: Icon(Icons.close_rounded, size: 18, color: tokens.textTertiary),
                        onPressed: onClear,
                        tooltip: 'Clear',
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(minWidth: 36, minHeight: 36),
                      ),
                    ),
                ],
              ),
            ),
          ),

          // Close button (expanded)
          if (!isCompact)
            Semantics(
              label: 'Close search',
              child: IconButton(
                icon: Icon(Icons.close_rounded, color: tokens.textSecondary),
                onPressed: onDismiss,
                tooltip: 'Close',
              ),
            ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Search result row
// ---------------------------------------------------------------------------
class _SearchResultRow extends StatelessWidget {
  final SearchResultItem item;
  final VoidCallback onTap;

  const _SearchResultRow({
    required this.item,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    final semanticLabel = '${item.displayTitle}'
        '${item.format != null ? ', ${item.format}' : ''}'
        '${item.seasonYear != null ? ', ${item.seasonYear}' : ''}';

    return MergeSemantics(
      child: Semantics(
        label: semanticLabel,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(tokens.radiusSm),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
            child: Row(
              children: [
                // Mini poster
                ClipRRect(
                  borderRadius: BorderRadius.circular(tokens.radiusSm),
                  child: SizedBox(
                    width: 48,
                    height: 72,
                    child: CachedNetworkImage(
                      imageUrl: item.coverImageSmall ?? '',
                      fit: BoxFit.cover,
                      errorWidget: (_, __, ___) => Container(
                        color: tokens.bgSurfaceAlt,
                        child: Icon(Icons.movie_outlined, size: 20, color: tokens.textTertiary),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),

                // Title + meta
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item.displayTitle,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          fontSize: 15,
                          fontWeight: FontWeight.w500,
                          color: tokens.textPrimary,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          if (item.format != null)
                            StatusPill(status: item.format!, fontSize: 10),
                          if (item.seasonYear != null) ...[
                            const SizedBox(width: 8),
                            Text(
                              '${item.seasonYear}',
                              style: TextStyle(
                                fontFamily: 'Plus Jakarta Sans',
                                fontSize: 12,
                                color: tokens.textTertiary,
                              ),
                            ),
                          ],
                          if (item.averageScore != null) ...[
                            const SizedBox(width: 8),
                            ScoreChip(score: item.averageScore, size: 32, compact: true),
                          ],
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
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
/// Returns an icon appropriate for the given media type string.
IconData _mediaTypeIcon(String mediaType) {
  switch (mediaType) {
    case 'anime':
      return Icons.videocam_rounded;
    case 'manga':
    case 'manhwa':
      return Icons.menu_book_rounded;
    case 'light_novel':
      return Icons.auto_stories_rounded;
    default:
      return Icons.search;
  }
}
