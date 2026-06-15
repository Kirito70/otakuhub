import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/tracking/models/list_entry.dart';

/// Current selected status tab
final activeStatusProvider = StateProvider<String>((ref) => 'watching');

/// Fetch list entries by status from GET /api/v1/lists/me
final listEntriesProvider =
    FutureProvider.family<List<ListEntry>, String>((ref, status) async {
  final api = ref.read(apiClientProvider);

  // For "plan" display group, merge plan_to_watch and plan_to_read
  if (status == 'plan') {
    final watchResp = await api.get<Map<String, dynamic>>(
      ApiEndpoints.listsMe,
      queryParameters: {'status': 'plan_to_watch', 'limit': 200},
    );
    final readResp = await api.get<Map<String, dynamic>>(
      ApiEndpoints.listsMe,
      queryParameters: {'status': 'plan_to_read', 'limit': 200},
    );
    final watchItems = _parseItems(watchResp.data);
    final readItems = _parseItems(readResp.data);
    return [...watchItems, ...readItems];
  }

  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.listsMe,
      queryParameters: {'status': status, 'limit': 200},
    );
    return _parseItems(response.data);
  } on DioException {
    return [];
  }
});

/// Fetch list statistics
final listStatsProvider = FutureProvider<ListStats>((ref) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.listsStats,
    );
    if (response.data == null) return const ListStats();
    return ListStats.fromJson(response.data!);
  } on DioException {
    return const ListStats();
  }
});

/// Fetch history
final listHistoryProvider = FutureProvider<List<HistoryItem>>((ref) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.listsHistory,
      queryParameters: {'limit': 50},
    );
    final data = response.data;
    if (data == null) return [];
    final items = data['items'] as List<dynamic>? ?? [];
    return items
        .map((e) => HistoryItem.fromJson(e as Map<String, dynamic>))
        .toList();
  } on DioException {
    return [];
  }
});

/// Invalidate all list data (for refresh)
final invalidateListDataProvider = Provider<void>((ref) {
  ref.invalidate(listStatsProvider);
  ref.invalidate(listHistoryProvider);
  final status = ref.read(activeStatusProvider);
  ref.invalidate(listEntriesProvider(status));
});

/// Update list entry progress
final updateProgressProvider =
    FutureProvider.family<void, ({String mediaId, int progress})>(
        (ref, params) async {
  final api = ref.read(apiClientProvider);
  await api.patch<Map<String, dynamic>>(
    '${ApiEndpoints.listsEntry}/${params.mediaId}',
    data: {'progress': params.progress},
  );
  ref.invalidate(listEntriesProvider(ref.read(activeStatusProvider)));
});

/// Update list entry score
final updateScoreProvider =
    FutureProvider.family<void, ({String mediaId, double? score})>(
        (ref, params) async {
  final api = ref.read(apiClientProvider);
  await api.patch<Map<String, dynamic>>(
    '${ApiEndpoints.listsEntry}/${params.mediaId}',
    data: {'score': params.score},
  );
  ref.invalidate(listEntriesProvider(ref.read(activeStatusProvider)));
});

/// Update list entry status
final updateStatusProvider =
    FutureProvider.family<void, ({String mediaId, String status})>(
        (ref, params) async {
  final api = ref.read(apiClientProvider);
  await api.patch<Map<String, dynamic>>(
    '${ApiEndpoints.listsEntry}/${params.mediaId}',
    data: {'status': params.status},
  );
  ref.invalidate(listEntriesProvider(ref.read(activeStatusProvider)));
  ref.invalidate(listStatsProvider);
});

/// Add media to list
final addToListProvider =
    FutureProvider.family<void, ({String mediaId, String status})>(
        (ref, params) async {
  final api = ref.read(apiClientProvider);
  await api.post<Map<String, dynamic>>(
    ApiEndpoints.listsEntry,
    data: {'media_id': params.mediaId, 'status': params.status},
  );
  ref.invalidate(listEntriesProvider(ref.read(activeStatusProvider)));
  ref.invalidate(listStatsProvider);
});

/// Delete list entry
final deleteEntryProvider =
    FutureProvider.family<void, String>((ref, mediaId) async {
  final api = ref.read(apiClientProvider);
  await api.delete<Map<String, dynamic>>(
    '${ApiEndpoints.listsEntry}/$mediaId',
  );
  ref.invalidate(listEntriesProvider(ref.read(activeStatusProvider)));
  ref.invalidate(listStatsProvider);
});

// --- Helpers ---

List<ListEntry> _parseItems(Map<String, dynamic>? data) {
  if (data == null) return [];
  final items = data['items'] as List<dynamic>? ?? [];
  return items
      .map((e) => ListEntry.fromJson(e as Map<String, dynamic>))
      .toList();
}
