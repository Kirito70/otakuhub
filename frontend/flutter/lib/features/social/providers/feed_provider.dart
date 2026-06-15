import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/feed_item.dart';

part 'feed_provider.g.dart';

const int _pageSize = 50;

/// Provider for the group activity feed (from shared-group members).
@riverpod
class GroupFeedNotifier extends _$GroupFeedNotifier {
  @override
  Future<FeedResponse> build() async {
    return _fetchFeed(0);
  }

  Future<FeedResponse> _fetchFeed(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.socialFeed,
      queryParameters: {'limit': _pageSize, 'offset': offset},
    );
    return FeedResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<FeedResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchFeed(data.items.length);
      final combined = FeedResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

/// Provider for "My Activity" (current user's own list history).
@riverpod
class MyActivityNotifier extends _$MyActivityNotifier {
  @override
  Future<FeedResponse> build() async {
    return _fetchMyActivity(0);
  }

  Future<FeedResponse> _fetchMyActivity(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.socialHistory,
      queryParameters: {'limit': _pageSize, 'offset': offset},
    );
    return FeedResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<FeedResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchMyActivity(data.items.length);
      final combined = FeedResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}
