/// Shared media item model for search results, trending, and seasonal lists.
class MediaItem {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String mediaType; // anime, manga, manhwa, etc.
  final String? format;   // TV, MOVIE, OVA, etc.
  final String status;
  final String? synopsis;
  final String? coverImageLarge;
  final String? coverImageMedium;
  final String? bannerImage;
  final double? averageScore;
  final int? popularity;
  final int? trending;
  final int? episodeCount;
  final int? chapterCount;
  final int? seasonYear;
  final String? season;
  final String? startDate;
  final String? endDate;
  final bool isAdult;

  const MediaItem({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    required this.mediaType,
    this.format,
    this.status = 'not_yet_released',
    this.synopsis,
    this.coverImageLarge,
    this.coverImageMedium,
    this.bannerImage,
    this.averageScore,
    this.popularity,
    this.trending,
    this.episodeCount,
    this.chapterCount,
    this.seasonYear,
    this.season,
    this.startDate,
    this.endDate,
    this.isAdult = false,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory MediaItem.fromJson(Map<String, dynamic> json) {
    return MediaItem(
      id: json['id'] as String,
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      mediaType: json['media_type'] as String? ?? 'unknown',
      format: json['format'] as String?,
      status: json['status'] as String? ?? 'not_yet_released',
      synopsis: json['synopsis'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      coverImageMedium: json['cover_image_medium'] as String?,
      bannerImage: json['banner_image'] as String?,
      averageScore: (json['average_score'] as num?)?.toDouble(),
      popularity: json['popularity'] as int?,
      trending: json['trending'] as int?,
      episodeCount: json['episode_count'] as int?,
      chapterCount: json['chapter_count'] as int?,
      seasonYear: json['season_year'] as int?,
      season: json['season'] as String?,
      startDate: json['start_date'] as String?,
      endDate: json['end_date'] as String?,
      isAdult: json['is_adult'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'title_romaji': titleRomaji,
        'title_english': titleEnglish,
        'media_type': mediaType,
        'format': format,
        'status': status,
        'synopsis': synopsis,
        'cover_image_large': coverImageLarge,
        'cover_image_medium': coverImageMedium,
        'banner_image': bannerImage,
        'average_score': averageScore,
        'popularity': popularity,
        'trending': trending,
        'episode_count': episodeCount,
        'chapter_count': chapterCount,
        'season_year': seasonYear,
        'season': season,
        'start_date': startDate,
        'end_date': endDate,
        'is_adult': isAdult,
      };
}
