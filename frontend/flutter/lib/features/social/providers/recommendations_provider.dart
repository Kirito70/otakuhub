import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/recommendation.dart';

part 'recommendations_provider.g.dart';

const int _pageSize = 50;

/// Provider for the current user's recommendation inbox.
@riverpod
class InboxNotifier extends _$InboxNotifier {
  @override
  Future<RecommendationListResponse> build() async {
    return _fetchInbox(0);
  }

  Future<RecommendationListResponse> _fetchInbox(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.socialRecInbox,
      queryParameters: {
        'limit': _pageSize,
        'offset': offset,
        'include_acknowledged': true,
      },
    );
    return RecommendationListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<RecommendationListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchInbox(data.items.length);
      final combined = RecommendationListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

/// Provider for the current user's sent recommendations.
@riverpod
class SentNotifier extends _$SentNotifier {
  @override
  Future<RecommendationListResponse> build() async {
    return _fetchSent(0);
  }

  Future<RecommendationListResponse> _fetchSent(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.socialRecSent,
      queryParameters: {'limit': _pageSize, 'offset': offset},
    );
    return RecommendationListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<RecommendationListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchSent(data.items.length);
      final combined = RecommendationListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

/// Acknowledge a recommendation (mark as seen).
@riverpod
class AcknowledgeAction extends _$AcknowledgeAction {
  @override
  Future<void> build() async {}

  Future<bool> acknowledge(String recommendationId) async {
    try {
      final dio = ref.read(apiClientProvider);
      await dio.patch<dynamic>(
        '${ApiEndpoints.socialRecInbox.replaceAll('/inbox', '')}/$recommendationId/acknowledge',
      );
      ref.invalidate(inboxNotifierProvider);
      ref.invalidate(sentNotifierProvider);
      return true;
    } on DioException {
      return false;
    }
  }
}

/// Create a recommendation.
@riverpod
class CreateRecommendationAction extends _$CreateRecommendationAction {
  @override
  Future<void> build() async {}

  Future<bool> create(CreateRecommendationRequest request) async {
    try {
      final dio = ref.read(apiClientProvider);
      await dio.post<dynamic>(
        ApiEndpoints.socialRecommend,
        data: request.toJson(),
      );
      ref.invalidate(sentNotifierProvider);
      return true;
    } on DioException {
      return false;
    }
  }
}
