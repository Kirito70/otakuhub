import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/discover/models/search_data.dart';

/// The current raw search query string (updated by the search bar).
final searchQueryProvider = StateProvider<String>((ref) => '');

/// Debounced search query (300ms delay).
final debouncedSearchQueryProvider = Provider<String>((ref) {
  return ref.watch(searchQueryProvider);
});

/// Provider that fetches search results from the global search endpoint.
///
/// Calls GET /api/v1/search?q={query}&limit=20 for the overlay.
/// Returns empty results on 404 (endpoint not yet built).
final globalSearchProvider =
    FutureProvider.family<SearchResults, String>((ref, query) async {
  if (query.trim().isEmpty) return const SearchResults();

  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.search,
      queryParameters: {
        'q': query.trim(),
        'limit': 20, // show all results inline
      },
    );
    final data = response.data;
    if (data == null) return const SearchResults();
    return SearchResults.fromJson(data);
  } on DioException catch (e) {
    if (e.response?.statusCode == 404) {
      return const SearchResults();
    }
    rethrow;
  }
});

/// Controller that manages the debounce timer for search input.
final searchDebounceProvider = Provider<SearchDebounceController>((ref) {
  return SearchDebounceController(ref);
});

class SearchDebounceController {
  final Ref _ref;
  Timer? _timer;

  SearchDebounceController(this._ref);

  void onQueryChanged(String query) {
    _timer?.cancel();
    _timer = Timer(const Duration(milliseconds: 300), () {
      _ref.read(searchQueryProvider.notifier).state = query;
    });
  }

  void dispose() {
    _timer?.cancel();
  }
}
