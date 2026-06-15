import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/discover/models/media_item.dart';

// --- State for search ---
final searchQueryProvider = StateProvider<String>((ref) => '');
final searchTypeProvider = StateProvider<String?>((ref) => null);

final searchResultsProvider = FutureProvider<List<MediaItem>>((ref) async {
  final query = ref.watch(searchQueryProvider);
  if (query.trim().isEmpty) return [];

  final api = ref.read(apiClientProvider);
  final params = <String, dynamic>{'query': query.trim()};
  final type = ref.watch(searchTypeProvider);
  if (type != null) params['type'] = type;

  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.mediaSearch,
      queryParameters: params,
    );
    final data = response.data;
    if (data == null) return [];
    final results = data['results'] as List<dynamic>? ?? data['items'] as List<dynamic>? ?? [];
    return results
        .map((e) => MediaItem.fromJson(e as Map<String, dynamic>))
        .toList();
  } on DioException {
    return [];
  }
});

// --- Trending ---
final trendingProvider = FutureProvider<List<MediaItem>>((ref) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.mediaTrending,
    );
    final data = response.data;
    if (data == null) return [];
    final results = data['results'] as List<dynamic>? ?? data['items'] as List<dynamic>? ?? [];
    return results
        .map((e) => MediaItem.fromJson(e as Map<String, dynamic>))
        .toList();
  } on DioException {
    return [];
  }
});

// --- Seasonal (new releases) ---
final seasonalProvider = FutureProvider<List<MediaItem>>((ref) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.mediaSeasonal,
    );
    final data = response.data;
    if (data == null) return [];
    final results = data['results'] as List<dynamic>? ?? data['items'] as List<dynamic>? ?? [];
    return results
        .map((e) => MediaItem.fromJson(e as Map<String, dynamic>))
        .toList();
  } on DioException {
    return [];
  }
});
