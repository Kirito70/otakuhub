import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/discover/models/home_data.dart';

/// Provider that fetches the composite home payload.
///
/// Calls GET /api/v1/home which aggregates spotlight, continue-watching,
/// friend recommendations, group watching, airing soon, and trending.
///
/// The provider is invalidated on pull-to-refresh via [homeInvalidatorProvider].
final homeProvider = FutureProvider<HomeData>((ref) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.home,
    );
    final data = response.data;
    if (data == null) return const HomeData();
    return HomeData.fromJson(data);
  } on DioException catch (e) {
    // If the home endpoint doesn't exist yet (404), return empty data
    // so the screen renders with a friendly empty state.
    if (e.response?.statusCode == 404) {
      return const HomeData();
    }
    rethrow;
  }
});

/// A simple state provider that increments when the user pulls to refresh.
/// The home screen writes to this, and the homeProvider watches it
/// so it re-fetches the data.
final homeRefreshProvider = StateProvider<int>((ref) => 0);

/// Invalidator: call `ref.read(homeInvalidatorProvider.notifier).refresh()`
/// to trigger a full re-fetch of home data.
final homeInvalidatorProvider = Provider<HomeInvalidator>((ref) {
  return HomeInvalidator(ref);
});

class HomeInvalidator {
  final Ref _ref;
  HomeInvalidator(this._ref);

  void refresh() {
    _ref.invalidate(homeProvider);
  }
}
