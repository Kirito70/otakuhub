/// ADR 094 Section 6.4 — Unified List page data models.
///
/// Covers filter state, browse results, curated rails.
library;

// ---------------------------------------------------------------------------
// Filter state — 8 filter types (Section 6.4.1)
// ---------------------------------------------------------------------------
class FilterState {
  final String mediaType; // 'all', 'anime', 'manga', 'manhwa', 'light_novel'
  final String status; // 'all', 'watching', 'reading', 'completed', 'paused', 'dropped', 'plan'
  final List<String> genres; // genre slugs
  final String format; // 'all', 'TV', 'MOVIE', 'OVA', 'ONA', 'SPECIAL', 'MUSIC'
  final String season; // 'all', 'spring_2026', 'winter_2026', ...
  final int? year;
  final String sort; // 'score_desc', 'score_asc', 'title_asc', 'popularity', 'trending', 'recently_updated', 'recently_added'
  final String? cursor;

  const FilterState({
    this.mediaType = 'all',
    this.status = 'all',
    this.genres = const [],
    this.format = 'all',
    this.season = 'all',
    this.year,
    this.sort = 'score_desc',
    this.cursor,
  });

  FilterState copyWith({
    String? mediaType,
    String? status,
    List<String>? genres,
    String? format,
    String? season,
    int? year,
    String? sort,
    String? cursor,
    bool clearCursor = false,
  }) {
    return FilterState(
      mediaType: mediaType ?? this.mediaType,
      status: status ?? this.status,
      genres: genres ?? this.genres,
      format: format ?? this.format,
      season: season ?? this.season,
      year: year ?? this.year,
      sort: sort ?? this.sort,
      cursor: clearCursor ? null : (cursor ?? this.cursor),
    );
  }

  /// Number of active (non-default) filters.
  int get activeFilterCount {
    int count = 0;
    if (mediaType != 'all') count++;
    if (status != 'all') count++;
    if (genres.isNotEmpty) count++;
    if (format != 'all') count++;
    if (season != 'all') count++;
    if (year != null) count++;
    if (sort != 'score_desc' && sort != 'recently_updated') count++;
    return count;
  }

  bool get hasActiveFilters => activeFilterCount > 0;

  /// Build query parameters for API calls.
  Map<String, dynamic> toQueryParams() {
    final params = <String, dynamic>{};
    if (mediaType != 'all') params['type'] = mediaType;
    if (status != 'all') params['status'] = status;
    if (genres.isNotEmpty) params['genre'] = genres.join(',');
    if (format != 'all') params['format'] = format;
    if (season != 'all') params['season'] = season;
    if (year != null) params['year'] = year;
    params['sort'] = sort;
    if (cursor != null) params['cursor'] = cursor;
    params['limit'] = 50;
    return params;
  }

  /// Reset all filters to default.
  FilterState clearAll() => const FilterState();

  static const List<String> mediaTypes = [
    'all', 'anime', 'manga', 'manhwa', 'light_novel',
  ];

  static const List<String> statuses = [
    'all', 'watching', 'reading', 'completed', 'paused', 'dropped', 'plan',
  ];

  static const List<String> formats = [
    'all', 'TV', 'MOVIE', 'OVA', 'ONA', 'SPECIAL', 'MUSIC',
  ];

  static const List<String> sortOptions = [
    'score_desc', 'score_asc', 'title_asc', 'popularity', 'trending',
    'recently_updated', 'recently_added',
  ];
}

// ---------------------------------------------------------------------------
// Browse result item (for Discover sub-tab + search results)
// ---------------------------------------------------------------------------
class BrowseResultItem {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageMedium;
  final String? coverImageLarge;
  final String? format;
  final String? mediaType;
  final int? seasonYear;
  final double? averageScore;
  final int? episodeCount;
  final int? chapterCount;

  const BrowseResultItem({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageMedium,
    this.coverImageLarge,
    this.format,
    this.mediaType,
    this.seasonYear,
    this.averageScore,
    this.episodeCount,
    this.chapterCount,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory BrowseResultItem.fromJson(Map<String, dynamic> json) {
    return BrowseResultItem(
      id: json['id'] as String,
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageMedium: json['cover_image_medium'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      format: json['format'] as String?,
      mediaType: json['media_type'] as String?,
      seasonYear: json['season_year'] as int?,
      averageScore: (json['average_score'] as num?)?.toDouble(),
      episodeCount: json['episode_count'] as int?,
      chapterCount: json['chapter_count'] as int?,
    );
  }

  String? get coverImage => coverImageMedium ?? coverImageLarge;
}

// ---------------------------------------------------------------------------
// Paginated browse response
// ---------------------------------------------------------------------------
class BrowseResponse {
  final List<BrowseResultItem> items;
  final int total;
  final String? nextCursor;

  const BrowseResponse({
    this.items = const [],
    this.total = 0,
    this.nextCursor,
  });

  factory BrowseResponse.fromJson(Map<String, dynamic> json) {
    final itemsList = (json['items'] as List<dynamic>?)
            ?.map((e) => BrowseResultItem.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    return BrowseResponse(
      items: itemsList,
      total: json['total'] as int? ?? itemsList.length,
      nextCursor: json['next_cursor'] as String?,
    );
  }
}

// ---------------------------------------------------------------------------
// Curated rails for Discover default state
// ---------------------------------------------------------------------------
class CuratedRails {
  final List<CuratedRail> rails;

  const CuratedRails({this.rails = const []});

  factory CuratedRails.fromJson(Map<String, dynamic> json) {
    final railsList = (json['rails'] as List<dynamic>?)
            ?.map((e) => CuratedRail.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    return CuratedRails(rails: railsList);
  }
}

class CuratedRail {
  final String title;
  final String railId;
  final List<BrowseResultItem> items;

  const CuratedRail({
    required this.title,
    required this.railId,
    this.items = const [],
  });

  factory CuratedRail.fromJson(Map<String, dynamic> json) {
    final itemsList = (json['items'] as List<dynamic>?)
            ?.map((e) => BrowseResultItem.fromJson(e as Map<String, dynamic>))
            .toList() ??
        [];
    return CuratedRail(
      title: json['title'] as String? ?? '',
      railId: json['rail_id'] as String? ?? '',
      items: itemsList,
    );
  }
}

// ---------------------------------------------------------------------------
// Sub-tab enum
// ---------------------------------------------------------------------------
enum ListPageTab { yourList, discover, calendar }
