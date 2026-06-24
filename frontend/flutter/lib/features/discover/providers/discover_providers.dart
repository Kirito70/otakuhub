import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/discover/models/media_item.dart';

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
