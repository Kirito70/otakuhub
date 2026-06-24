import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';
import 'package:otakuhub/core/widgets/focusable_widget.dart';
import 'package:otakuhub/features/tracking/models/list_page_data.dart';
import 'package:otakuhub/features/tracking/providers/filter_provider.dart';

/// ADR 094 Section 6.4.1 — Sticky Filter Bar.
///
/// A horizontal scrollable row of pill-shaped filter chips, pinned below the
/// tab bar. Active filters appear as removable chips below. The bar is sticky
/// — stays visible as the grid scrolls.
///
/// Built as a widget (not a component) because it's specific to the List page,
/// though the `/search` results page reuses the same filter chips.
class ListFilterBar extends ConsumerWidget {
  final ListPageTab currentTab;

  const ListFilterBar({super.key, required this.currentTab});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return _FilterBarContent(currentTab: currentTab);
  }
}

class _FilterBarContent extends ConsumerWidget {
  final ListPageTab currentTab;

  const _FilterBarContent({required this.currentTab});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tokens = context.tokens;
    final filterState = ref.watch(filterStateProvider);

    return ScrollConfiguration(
      behavior: ScrollConfiguration.of(context).copyWith(scrollbars: false),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // --- Main filter row (horizontal scrollable chips) ---
          SizedBox(
            height: 44,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: EdgeInsets.symmetric(horizontal: tokens.spaceMd),
              children: [
                FocusableWidget(
                  child: _FilterChip(
                    label: filterState.mediaType == 'all'
                        ? 'Media Type'
                        : _mediaTypeDisplay(filterState.mediaType),
                    active: filterState.mediaType != 'all',
                    options: FilterState.mediaTypes,
                    currentValue: filterState.mediaType,
                    onSelected: (value) {
                      ref.read(filterStateProvider.notifier).state =
                          filterState.copyWith(mediaType: value, clearCursor: true);
                    },
                    displayFn: _mediaTypeDisplay,
                  ),
                ),

                if (currentTab == ListPageTab.yourList)
                  FocusableWidget(
                    child: _FilterChip(
                      label: filterState.status == 'all'
                          ? 'Status'
                          : _statusDisplay(filterState.status),
                      active: filterState.status != 'all',
                      options: FilterState.statuses,
                      currentValue: filterState.status,
                      onSelected: (value) {
                        ref.read(filterStateProvider.notifier).state =
                            filterState.copyWith(status: value, clearCursor: true);
                      },
                      displayFn: _statusDisplay,
                    ),
                  ),

                if (currentTab != ListPageTab.yourList)
                  FocusableWidget(
                    child: _FilterChip(
                      label: filterState.genres.isEmpty
                          ? 'Genre'
                          : '${filterState.genres.length} genre${filterState.genres.length == 1 ? '' : 's'}',
                      active: filterState.genres.isNotEmpty,
                      // Genre selection uses a bottom sheet, not inline pills
                      onTap: () {
                        _showGenreSheet(context, ref, filterState);
                      },
                    ),
                  ),

                FocusableWidget(
                  child: _FilterChip(
                    label: filterState.format == 'all'
                        ? 'Format'
                        : filterState.format,
                    active: filterState.format != 'all',
                    options: FilterState.formats,
                    currentValue: filterState.format,
                    onSelected: (value) {
                      ref.read(filterStateProvider.notifier).state =
                          filterState.copyWith(format: value, clearCursor: true);
                    },
                    displayFn: (v) => v,
                  ),
                ),

                FocusableWidget(
                  child: _FilterChip(
                    label: filterState.season == 'all'
                        ? 'Season'
                        : _seasonDisplay(filterState.season),
                    active: filterState.season != 'all',
                    options: _seasonOptions,
                    currentValue: filterState.season,
                    onSelected: (value) {
                      ref.read(filterStateProvider.notifier).state =
                          filterState.copyWith(season: value, clearCursor: true);
                    },
                    displayFn: _seasonDisplay,
                  ),
                ),

                FocusableWidget(
                  child: _FilterChip(
                    label: filterState.year?.toString() ?? 'Year',
                    active: filterState.year != null,
                    options: _yearOptions,
                    currentValue: filterState.year?.toString() ?? 'all',
                    onSelected: (value) {
                      ref.read(filterStateProvider.notifier).state =
                          filterState.copyWith(
                        year: value == 'all' ? null : int.tryParse(value),
                        clearCursor: true,
                      );
                    },
                    displayFn: (v) => v == 'all' ? 'Year' : v,
                  ),
                ),

                FocusableWidget(
                  child: _FilterChip(
                    label: _sortDisplay(filterState.sort),
                    active: filterState.sort != 'score_desc' &&
                        filterState.sort != 'recently_updated',
                    options: FilterState.sortOptions,
                    currentValue: filterState.sort,
                    onSelected: (value) {
                      ref.read(filterStateProvider.notifier).state =
                          filterState.copyWith(sort: value, clearCursor: true);
                    },
                    displayFn: _sortDisplay,
                  ),
                ),
              ],
            ),
          ),

          // --- Active filter chips (removable) ---
          if (filterState.hasActiveFilters)
            Container(
              height: 36,
              padding: EdgeInsets.symmetric(horizontal: tokens.spaceMd),
              child: Row(
                children: [
                  Expanded(
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        if (filterState.mediaType != 'all')
                          _ActiveChip(
                            label: _mediaTypeDisplay(filterState.mediaType),
                            onRemove: () {
                              ref.read(filterStateProvider.notifier).state =
                                  filterState.copyWith(mediaType: 'all', clearCursor: true);
                            },
                          ),
                        if (filterState.status != 'all' && currentTab == ListPageTab.yourList)
                          _ActiveChip(
                            label: _statusDisplay(filterState.status),
                            onRemove: () {
                              ref.read(filterStateProvider.notifier).state =
                                  filterState.copyWith(status: 'all', clearCursor: true);
                            },
                          ),
                        if (filterState.genres.isNotEmpty)
                          ...filterState.genres.map((g) => _ActiveChip(
                                label: g,
                                onRemove: () {
                                  ref.read(filterStateProvider.notifier).state =
                                      filterState.copyWith(
                                    genres: filterState.genres.where((x) => x != g).toList(),
                                    clearCursor: true,
                                  );
                                },
                              )),
                        if (filterState.format != 'all')
                          _ActiveChip(
                            label: filterState.format,
                            onRemove: () {
                              ref.read(filterStateProvider.notifier).state =
                                  filterState.copyWith(format: 'all', clearCursor: true);
                            },
                          ),
                        if (filterState.season != 'all')
                          _ActiveChip(
                            label: _seasonDisplay(filterState.season),
                            onRemove: () {
                              ref.read(filterStateProvider.notifier).state =
                                  filterState.copyWith(season: 'all', clearCursor: true);
                            },
                          ),
                        if (filterState.year != null)
                          _ActiveChip(
                            label: '${filterState.year}',
                            onRemove: () {
                              ref.read(filterStateProvider.notifier).state =
                                  filterState.copyWith(year: null, clearCursor: true);
                            },
                          ),
                      ],
                    ),
                  ),
                  if (filterState.activeFilterCount >= 2)
                    GestureDetector(
                      onTap: () => ref.read(filterStateProvider.notifier).state =
                          const FilterState(),
                      child: Text(
                        'Clear all',
                        style: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: tokens.accentPrimary,
                        ),
                      ),
                    ),
                  SizedBox(width: tokens.spaceSm),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Filter chip widget
// ---------------------------------------------------------------------------
class _FilterChip extends StatelessWidget {
  final String label;
  final bool active;
  final List<String>? options;
  final String? currentValue;
  final ValueChanged<String>? onSelected;
  final VoidCallback? onTap;
  final String Function(String)? displayFn;

  const _FilterChip({
    required this.label,
    this.active = false,
    this.options,
    this.currentValue,
    this.onSelected,
    this.onTap,
    this.displayFn,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: GestureDetector(
        onTap: () {
          if (onTap != null) {
            onTap!();
          } else if (options != null && onSelected != null && currentValue != null) {
            _showOptionsSheet(context);
          }
        },
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: active ? tokens.accentPrimary.withValues(alpha: 0.14) : tokens.bgSurfaceAlt,
            borderRadius: BorderRadius.circular(tokens.radiusXl),
            border: Border.all(
              color: active ? tokens.accentPrimary.withValues(alpha: 0.3) : tokens.borderSubtle,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (active)
                Padding(
                  padding: const EdgeInsets.only(right: 6),
                  child: Icon(Icons.check_circle_rounded, size: 14, color: tokens.accentPrimary),
                ),
              Text(
                label,
                style: TextStyle(
                  fontFamily: 'Plus Jakarta Sans',
                  fontSize: 12,
                  fontWeight: active ? FontWeight.w600 : FontWeight.w500,
                  color: active ? tokens.accentPrimary : tokens.textSecondary,
                ),
              ),
              const SizedBox(width: 4),
              Icon(
                Icons.arrow_drop_down_rounded,
                size: 16,
                color: active ? tokens.accentPrimary : tokens.textTertiary,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showOptionsSheet(BuildContext context) {
    final tokens = context.tokens;
    showModalBottomSheet(
      context: context,
      backgroundColor: tokens.bgElevated,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) {
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
              width: 32,
              height: 4,
              decoration: BoxDecoration(
                color: tokens.textTertiary.withValues(alpha: 0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 16),
            ...?options?.map((option) {
              final isSelected = option == currentValue;
              return ListTile(
                leading: isSelected
                    ? Icon(Icons.check_rounded, color: tokens.accentPrimary, size: 20)
                    : const SizedBox(width: 20),
                title: Text(
                  displayFn?.call(option) ?? option,
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 15,
                    fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                    color: isSelected ? tokens.accentPrimary : tokens.textPrimary,
                  ),
                ),
                onTap: () {
                  onSelected?.call(option);
                  Navigator.pop(ctx);
                },
              );
            }),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 8),
          ],
        );
      },
    );
  }
}

// ---------------------------------------------------------------------------
// Active (removable) chip
// ---------------------------------------------------------------------------
class _ActiveChip extends StatelessWidget {
  final String label;
  final VoidCallback onRemove;

  const _ActiveChip({required this.label, required this.onRemove});

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: tokens.accentPrimary.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(tokens.radiusSm),
          border: Border.all(color: tokens.accentPrimary.withValues(alpha: 0.2)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: 11,
                fontWeight: FontWeight.w500,
                color: tokens.accentPrimary,
              ),
            ),
            const SizedBox(width: 4),
            GestureDetector(
              onTap: onRemove,
              child: Icon(Icons.close_rounded, size: 14, color: tokens.accentPrimary),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Display helpers
// ---------------------------------------------------------------------------
String _mediaTypeDisplay(String type) {
  switch (type) {
    case 'anime':
      return 'Anime';
    case 'manga':
      return 'Manga';
    case 'manhwa':
      return 'Manhwa';
    case 'light_novel':
      return 'Light Novel';
    case 'all':
      return 'Media Type';
    default:
      return type;
  }
}

String _statusDisplay(String status) {
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
    case 'plan':
      return 'Plan';
    case 'all':
      return 'Status';
    default:
      return status;
  }
}

String _seasonDisplay(String season) {
  if (season == 'all') return 'Season';
  final parts = season.split('_');
  if (parts.length == 2) {
    return '${_capitalize(parts[0])} ${parts[1]}';
  }
  return season;
}

String _sortDisplay(String sort) {
  switch (sort) {
    case 'score_desc':
      return 'Score (high)';
    case 'score_asc':
      return 'Score (low)';
    case 'title_asc':
      return 'Title A-Z';
    case 'popularity':
      return 'Popularity';
    case 'trending':
      return 'Trending';
    case 'recently_updated':
      return 'Recently Updated';
    case 'recently_added':
      return 'Recently Added';
    default:
      return 'Sort';
  }
}

String _capitalize(String s) {
  if (s.isEmpty) return s;
  return s[0].toUpperCase() + s.substring(1);
}

/// Season options: last 2 years + next year
List<String> get _seasonOptions {
  final now = DateTime.now();
  final currentYear = now.year;
  final seasons = ['winter', 'spring', 'summer', 'fall'];
  final options = <String>['all'];
  for (final year in [currentYear - 1, currentYear, currentYear + 1]) {
    for (final season in seasons) {
      options.add('${season}_$year');
    }
  }
  return options;
}

/// Year options: last 5 years through next year
List<String> get _yearOptions {
  final now = DateTime.now();
  return [
    'all',
    for (var y = now.year + 1; y >= now.year - 5; y--) y.toString(),
  ];
}

/// Genre selection bottom sheet (called by Genre chip onTap).
void _showGenreSheet(BuildContext context, WidgetRef ref, FilterState filterState) {
  final tokens = context.tokens;
  // Pre-defined common genres — eventually fetched from /api/v1/media/genres
  const allGenres = [
    'Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy', 'Horror',
    'Mystery', 'Romance', 'Sci-Fi', 'Slice of Life', 'Sports', 'Supernatural',
    'Thriller', 'Ecchi', 'Mecha', 'Music', 'Psychological', 'Seinen',
    'Shoujo', 'Shounen', 'Isekai',
  ];

  showModalBottomSheet(
    context: context,
    backgroundColor: tokens.bgElevated,
    isScrollControlled: true,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
    ),
    builder: (ctx) {
      return DraggableScrollableSheet(
        initialChildSize: 0.5,
        minChildSize: 0.3,
        maxChildSize: 0.7,
        expand: false,
        builder: (ctx, scrollController) {
          return Column(
            children: [
              const SizedBox(height: 12),
              Container(
                width: 32,
                height: 4,
                decoration: BoxDecoration(
                  color: tokens.textTertiary.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                child: Row(
                  children: [
                    Text(
                      'Genres',
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: tokens.textPrimary,
                      ),
                    ),
                    const Spacer(),
                    if (filterState.genres.isNotEmpty)
                      GestureDetector(
                        onTap: () {
                          ref.read(filterStateProvider.notifier).state =
                              filterState.copyWith(genres: [], clearCursor: true);
                          Navigator.pop(ctx);
                        },
                        child: Text(
                          'Clear',
                          style: TextStyle(
                            fontFamily: 'Plus Jakarta Sans',
                            fontSize: 13,
                            color: tokens.accentPrimary,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
              const Divider(height: 1),
              Expanded(
                child: GridView.builder(
                  controller: scrollController,
                  padding: const EdgeInsets.all(16),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 3,
                    childAspectRatio: 3,
                    crossAxisSpacing: 8,
                    mainAxisSpacing: 8,
                  ),
                  itemCount: allGenres.length,
                  itemBuilder: (ctx, i) {
                    final genre = allGenres[i];
                    final isSelected = filterState.genres.contains(genre);
                    return GestureDetector(
                      onTap: () {
                        final newGenres = isSelected
                            ? filterState.genres.where((g) => g != genre).toList()
                            : [...filterState.genres, genre];
                        ref.read(filterStateProvider.notifier).state =
                            filterState.copyWith(genres: newGenres, clearCursor: true);
                      },
                      child: Container(
                        decoration: BoxDecoration(
                          color: isSelected
                              ? tokens.accentPrimary.withValues(alpha: 0.14)
                              : tokens.bgSurfaceAlt,
                          borderRadius: BorderRadius.circular(tokens.radiusMd),
                          border: Border.all(
                            color: isSelected
                                ? tokens.accentPrimary.withValues(alpha: 0.3)
                                : tokens.borderSubtle,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            genre,
                            style: TextStyle(
                              fontFamily: 'Plus Jakarta Sans',
                              fontSize: 12,
                              fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                              color: isSelected ? tokens.accentPrimary : tokens.textSecondary,
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
      );
    },
  );
}
