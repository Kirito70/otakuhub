import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/media_detail/models/media_detail.dart';

/// Provider for media detail by ID.
/// GET /api/v1/media/{id} -> MediaDetailResponse (single object)
final mediaDetailProvider =
    FutureProvider.family<MediaDetail?, String>((ref, mediaId) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      '${ApiEndpoints.mediaDetail}/$mediaId',
    );
    if (response.data == null) return null;
    return MediaDetail.fromJson(response.data!);
  } on DioException {
    return null;
  }
});

/// Provider for episodes by media ID.
/// GET /api/v1/media/{id}/episodes -> EpisodeListResponse { items: [EpisodeItem] }
final episodesProvider =
    FutureProvider.family<List<EpisodeInfo>, String>((ref, mediaId) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      '${ApiEndpoints.mediaDetail}/$mediaId/episodes',
    );
    final data = response.data;
    if (data == null) return [];
    final results = data['items'] as List<dynamic>? ?? [];
    return results
        .map((e) => EpisodeInfo.fromJson(e as Map<String, dynamic>))
        .toList();
  } on DioException {
    return [];
  }
});

/// Provider for relations by media ID.
/// GET /api/v1/media/{id}/relations -> { items: [RelatedMediaItem] }
final mediaRelationsProvider =
    FutureProvider.family<List<MediaRelation>, String>((ref, mediaId) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      '${ApiEndpoints.mediaDetail}/$mediaId/relations',
    );
    final data = response.data;
    if (data == null) return [];
    final results = data['items'] as List<dynamic>? ?? [];
    return results
        .map((e) => MediaRelation.fromJson(e as Map<String, dynamic>))
        .toList();
  } on DioException {
    return [];
  }
});
