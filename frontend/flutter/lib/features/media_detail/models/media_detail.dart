/// Full media detail model returned from GET /api/v1/media/{id}
class MediaDetail {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? titleNative;
  final String mediaType;
  final String? format;
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
  final int? volumeCount;
  final int? durationMinutes;
  final int? seasonYear;
  final String? season;
  final String? startDate;
  final String? endDate;
  final bool isAdult;
  final String? countryOfOrigin;
  final List<GenreInfo>? genres;

  const MediaDetail({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.titleNative,
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
    this.volumeCount,
    this.durationMinutes,
    this.seasonYear,
    this.season,
    this.startDate,
    this.endDate,
    this.isAdult = false,
    this.countryOfOrigin,
    this.genres,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory MediaDetail.fromJson(Map<String, dynamic> json) {
    return MediaDetail(
      id: json['id'] as String,
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      titleNative: json['title_native'] as String?,
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
      volumeCount: json['volume_count'] as int?,
      durationMinutes: json['duration_minutes'] as int?,
      seasonYear: json['season_year'] as int?,
      season: json['season'] as String?,
      startDate: json['start_date'] as String?,
      endDate: json['end_date'] as String?,
      isAdult: json['is_adult'] as bool? ?? false,
      countryOfOrigin: json['country_of_origin'] as String?,
      genres: (json['genres'] as List<dynamic>?)
          ?.map((e) => GenreInfo.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class GenreInfo {
  final String id;
  final String name;
  final String? slug;

  const GenreInfo({required this.id, required this.name, this.slug});

  factory GenreInfo.fromJson(Map<String, dynamic> json) {
    return GenreInfo(
      id: json['id'] as String,
      name: json['name'] as String? ?? '',
      slug: json['slug'] as String?,
    );
  }
}

/// Related media from GET /api/v1/media/{id}/relations
/// API returns RelatedMediaItem with id = related media's UUID
class MediaRelation {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageMedium;
  final String? mediaType;
  final String relationType;

  const MediaRelation({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageMedium,
    this.mediaType,
    required this.relationType,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory MediaRelation.fromJson(Map<String, dynamic> json) {
    return MediaRelation(
      id: json['id'] as String,
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageMedium: json['cover_image_medium'] as String?,
      mediaType: json['media_type'] as String?,
      relationType: json['relation_type'] as String? ?? 'other',
    );
  }
}

/// Episode from GET /api/v1/media/{id}/episodes
/// API returns EpisodeListResponse { items: [EpisodeItem] }
class EpisodeInfo {
  final String id;
  final int episodeNumber;
  final String? title;
  final String? airDate;
  final int? durationMinutes;
  final String? thumbnailUrl;

  const EpisodeInfo({
    required this.id,
    required this.episodeNumber,
    this.title,
    this.airDate,
    this.durationMinutes,
    this.thumbnailUrl,
  });

  factory EpisodeInfo.fromJson(Map<String, dynamic> json) {
    return EpisodeInfo(
      id: json['id'] as String,
      episodeNumber: json['episode_number'] as int? ?? 0,
      title: json['title'] as String?,
      airDate: json['air_date'] as String?,
      durationMinutes: json['duration_minutes'] as int?,
      thumbnailUrl: json['thumbnail_url'] as String?,
    );
  }
}

class ChapterInfo {
  final String id;
  final double chapterNumber;
  final int? volumeNumber;
  final String? title;
  final String? publishedAt;

  const ChapterInfo({
    required this.id,
    required this.chapterNumber,
    this.volumeNumber,
    this.title,
    this.publishedAt,
  });

  factory ChapterInfo.fromJson(Map<String, dynamic> json) {
    return ChapterInfo(
      id: json['id'] as String,
      chapterNumber: (json['chapter_number'] as num?)?.toDouble() ?? 0,
      volumeNumber: json['volume_number'] as int?,
      title: json['title'] as String?,
      publishedAt: json['published_at'] as String?,
    );
  }
}
