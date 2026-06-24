import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/tracking/models/list_entry.dart';
import 'package:otakuhub/features/tracking/models/list_page_data.dart';
import 'package:otakuhub/features/tracking/providers/filter_provider.dart';

// ---------------------------------------------------------------------------
// Your List sub-tab
// ---------------------------------------------------------------------------
/// Fetches the user's list from /api/v1/lists/me with current filters applied.
final yourListProvider =
    FutureProvider<List<ListEntry>>((ref) async {
  final api = ref.read(apiClientProvider);
  final filters = ref.watch(filterStateProvider);

  try {
    final params = filters.toQueryParams();
    // Your List defaults to 'recently_updated' sort
    params['sort'] = filters.sort;
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.listsMe,
      queryParameters: params,
    );
    return _parseListEntries(response.data);
  } on DioException {
    return [];
  }
});

/// Your List stats — watching, completed, avg score.
final yourListStatsProvider = FutureProvider<ListStats>((ref) async {
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

// ---------------------------------------------------------------------------
// Discover sub-tab
// ---------------------------------------------------------------------------
/// Fetches browse results from /api/v1/media/browse with current filters.
final discoverProvider =
    FutureProvider<BrowseResponse>((ref) async {
  final api = ref.read(apiClientProvider);
  final filters = ref.watch(filterStateProvider);

  try {
    final params = filters.toQueryParams();
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.mediaBrowse,
      queryParameters: params,
    );
    if (response.data == null) return const BrowseResponse();
    return BrowseResponse.fromJson(response.data!);
  } on DioException {
    return const BrowseResponse();
  }
});

/// Curated rails for Discover (when no filters active).
final curatedRailsProvider = FutureProvider<CuratedRails>((ref) async {
  final api = ref.read(apiClientProvider);
  try {
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.mediaCuratedRails,
    );
    if (response.data == null) return const CuratedRails();
    return CuratedRails.fromJson(response.data!);
  } on DioException {
    return const CuratedRails();
  }
});

/// Whether Discover should show curated rails (no filters) or filtered grid.
final discoverShowRailsProvider = Provider<bool>((ref) {
  return !ref.watch(filterStateProvider).hasActiveFilters;
});

// ---------------------------------------------------------------------------
// Calendar sub-tab
// ---------------------------------------------------------------------------
/// Fetches airing/chapter schedule from /api/v1/calendar with current filters.
final calendarProvider = FutureProvider<List<CalendarEvent>>((ref) async {
  final api = ref.read(apiClientProvider);
  final filters = ref.watch(filterStateProvider);

  try {
    final params = <String, dynamic>{
      if (filters.mediaType != 'all') 'type': filters.mediaType,
      'limit': 100,
    };
    final response = await api.get<Map<String, dynamic>>(
      ApiEndpoints.calendar,
      queryParameters: params,
    );
    final data = response.data;
    if (data == null) return [];
    final items = data['items'] as List<dynamic>? ?? [];
    return items
        .map((e) => CalendarEvent.fromJson(e as Map<String, dynamic>))
        .toList();
  } on DioException {
    return [];
  }
});

// ---------------------------------------------------------------------------
// Models
// ---------------------------------------------------------------------------
class CalendarEvent {
  final String id;
  final String mediaId;
  final String title;
  final String? coverImage;
  final String? mediaType;
  final int? episodeNumber;
  final int? chapterNumber;
  final String airingAt;
  final String? format;

  const CalendarEvent({
    required this.id,
    required this.mediaId,
    required this.title,
    this.coverImage,
    this.mediaType,
    this.episodeNumber,
    this.chapterNumber,
    required this.airingAt,
    this.format,
  });

  factory CalendarEvent.fromJson(Map<String, dynamic> json) {
    return CalendarEvent(
      id: json['id'] as String? ?? '',
      mediaId: json['media_id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      coverImage: json['cover_image'] as String?,
      mediaType: json['media_type'] as String?,
      episodeNumber: json['episode_number'] as int?,
      chapterNumber: json['chapter_number'] as int?,
      airingAt: json['airing_at'] as String? ?? json['created_at'] as String? ?? '',
      format: json['format'] as String?,
    );
  }

  DateTime get airingAtDate => DateTime.tryParse(airingAt) ?? DateTime.now();
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
List<ListEntry> _parseListEntries(Map<String, dynamic>? data) {
  if (data == null) return [];
  final items = data['items'] as List<dynamic>? ?? [];
  return items
      .map((e) => ListEntry.fromJson(e as Map<String, dynamic>))
      .toList();
}
