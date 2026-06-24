import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/features/tracking/models/list_page_data.dart';

/// Filter state — drives all 3 sub-tabs on the List page.
///
/// Built as a plain StateProvider (the filter state is simple serializable,
/// does not need complex async actions).
final filterStateProvider = StateProvider<FilterState>((ref) => const FilterState());

/// Track the current sort mode per tab context.
/// Your List defaults to 'recently_updated', Discover defaults to 'score_desc'.
final filterSortByTabProvider = StateProvider.family<String, ListPageTab>((ref, tab) {
  switch (tab) {
    case ListPageTab.yourList:
      return 'recently_updated';
    case ListPageTab.discover:
      return 'score_desc';
    case ListPageTab.calendar:
      return 'recently_updated';
  }
});

/// Returns the number of active (non-default) filters.
final activeFilterCountProvider = Provider<int>((ref) {
  return ref.watch(filterStateProvider).activeFilterCount;
});

/// Clears all filters.
final clearAllFiltersProvider = Provider<void>((ref) {
  ref.read(filterStateProvider.notifier).state = const FilterState();
});
