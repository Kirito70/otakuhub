import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/discussion.dart';

part 'discussions_provider.g.dart';

const int _pageSize = 50;

/// Provider for discussions for a given media ID.
@riverpod
class DiscussionListNotifier extends _$DiscussionListNotifier {
  @override
  Future<DiscussionListResponse> build(String mediaId) async {
    if (mediaId.isEmpty) {
      return const DiscussionListResponse();
    }
    return _fetchDiscussions(mediaId, 0);
  }

  Future<DiscussionListResponse> _fetchDiscussions(
    String mediaId,
    int offset,
  ) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      '${ApiEndpoints.socialDiscussions}/$mediaId',
      queryParameters: {'limit': _pageSize, 'offset': offset},
    );
    return DiscussionListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore(String mediaId) async {
    final current = state;
    if (current is AsyncData<DiscussionListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchDiscussions(mediaId, data.items.length);
      final combined = DiscussionListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

/// Provider for replies to a specific discussion.
@riverpod
class ReplyListNotifier extends _$ReplyListNotifier {
  @override
  Future<ReplyListResponse> build(String discussionId) async {
    return _fetchReplies(discussionId, 0);
  }

  Future<ReplyListResponse> _fetchReplies(
    String discussionId,
    int offset,
  ) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      '${ApiEndpoints.socialDiscussions}/$discussionId/replies',
      queryParameters: {'limit': _pageSize, 'offset': offset},
    );
    return ReplyListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore(String discussionId) async {
    final current = state;
    if (current is AsyncData<ReplyListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchReplies(discussionId, data.items.length);
      final combined = ReplyListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

/// Create a new discussion.
@riverpod
class CreateDiscussionAction extends _$CreateDiscussionAction {
  @override
  Future<void> build() async {}

  Future<Discussion?> create(CreateDiscussionRequest request) async {
    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.post<dynamic>(
        ApiEndpoints.socialDiscussions,
        data: request.toJson(),
      );
      return Discussion.fromJson(response.data as Map<String, dynamic>);
    } on DioException {
      return null;
    }
  }
}

/// Create a reply to a discussion.
@riverpod
class CreateReplyAction extends _$CreateReplyAction {
  @override
  Future<void> build() async {}

  Future<bool> create(String discussionId, CreateReplyRequest request) async {
    try {
      final dio = ref.read(apiClientProvider);
      await dio.post<dynamic>(
        '${ApiEndpoints.socialDiscussions}/$discussionId/replies',
        data: request.toJson(),
      );
      ref.invalidate(replyListNotifierProvider(discussionId));
      return true;
    } on DioException {
      return false;
    }
  }
}
