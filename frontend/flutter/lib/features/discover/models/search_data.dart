/// ADR 094 Section 6.2 — Global Search models.
///
/// Shapes the response for GET /api/v1/search which returns results
/// grouped by media type (anime, manga, manhwa, light_novel).
class SearchResults {
  final List<SearchResultGroup> groups;
  final int totalCount;

  const SearchResults({
    this.groups = const [],
    this.totalCount = 0,
  });

  bool get isEmpty => groups.every((g) => g.items.isEmpty);

  factory SearchResults.fromJson(Map<String, dynamic> json) {
    final groups = <SearchResultGroup>[];
    int total = 0;

    for (final type in ['anime', 'manga', 'manhwa', 'light_novel']) {
      final items = (json[type] as List<dynamic>?)
              ?.map((e) =>
                  SearchResultItem.fromJson(e as Map<String, dynamic>, type))
              .toList() ??
          [];
      if (items.isNotEmpty || json['${type}_count'] != null) {
        final count = json['${type}_count'] as int? ?? items.length;
        groups.add(SearchResultGroup(
          mediaType: type,
          items: items,
          count: count,
        ));
        total += count;
      }
    }

    return SearchResults(
      groups: groups,
      totalCount: total,
    );
  }
}

class SearchResultGroup {
  final String mediaType;
  final List<SearchResultItem> items;
  final int count;

  const SearchResultGroup({
    required this.mediaType,
    this.items = const [],
    this.count = 0,
  });

  String get displayName {
    switch (mediaType) {
      case 'anime':
        return 'Anime';
      case 'manga':
        return 'Manga';
      case 'manhwa':
        return 'Manhwa';
      case 'light_novel':
        return 'Light Novels';
      default:
        return mediaType;
    }
  }

  bool get showViewAll => count > items.length;
}

class SearchResultItem {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageSmall;
  final String? format;
  final int? seasonYear;
  final double? averageScore;
  final String mediaType;

  const SearchResultItem({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageSmall,
    this.format,
    this.seasonYear,
    this.averageScore,
    this.mediaType = 'anime',
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory SearchResultItem.fromJson(
      Map<String, dynamic> json, String type) {
    return SearchResultItem(
      id: json['id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageSmall: json['cover_image_small'] as String?,
      format: json['format'] as String?,
      seasonYear: json['season_year'] as int?,
      averageScore: (json['average_score'] as num?)?.toDouble(),
      mediaType: type,
    );
  }
}
