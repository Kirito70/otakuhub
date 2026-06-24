/// ADR 094 Section 8.1 — Composite home payload models.
///
/// Shapes the response for GET /api/v1/home that the Home screen uses.
/// Each sub-model maps to a section on the home feed.

class HomeSpotlightItem {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? format;
  final int? seasonYear;
  final double? averageScore;
  final String? synopsis;
  final String? coverImageLarge;
  final String? bannerImage;
  final String? mediaType;

  const HomeSpotlightItem({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.format,
    this.seasonYear,
    this.averageScore,
    this.synopsis,
    this.coverImageLarge,
    this.bannerImage,
    this.mediaType,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory HomeSpotlightItem.fromJson(Map<String, dynamic> json) {
    return HomeSpotlightItem(
      id: json['id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      format: json['format'] as String?,
      seasonYear: json['season_year'] as int?,
      averageScore: (json['average_score'] as num?)?.toDouble(),
      synopsis: json['synopsis'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      bannerImage: json['banner_image'] as String?,
      mediaType: json['media_type'] as String?,
    );
  }
}

class HomeContinueItem {
  final String id;
  final String mediaId;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageLarge;
  final int progress;
  final int? maxProgress;
  final int? nextEpisodeNumber;
  final String? status;

  const HomeContinueItem({
    required this.id,
    required this.mediaId,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageLarge,
    required this.progress,
    this.maxProgress,
    this.nextEpisodeNumber,
    this.status,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory HomeContinueItem.fromJson(Map<String, dynamic> json) {
    return HomeContinueItem(
      id: json['id'] as String? ?? '',
      mediaId: json['media_id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      progress: json['progress'] as int? ?? 0,
      maxProgress: json['max_progress'] as int?,
      nextEpisodeNumber: json['next_episode_number'] as int?,
      status: json['status'] as String?,
    );
  }
}

class HomeFriendRecItem {
  final String id;
  final String mediaId;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageLarge;
  final double? averageScore;
  final String? fromUserId;
  final String? fromUsername;
  final String? fromDisplayName;
  final String? fromAvatarUrl;
  final String? message;

  const HomeFriendRecItem({
    required this.id,
    required this.mediaId,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageLarge,
    this.averageScore,
    this.fromUserId,
    this.fromUsername,
    this.fromDisplayName,
    this.fromAvatarUrl,
    this.message,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;
  String get fromName => fromDisplayName ?? fromUsername ?? 'A friend';

  factory HomeFriendRecItem.fromJson(Map<String, dynamic> json) {
    return HomeFriendRecItem(
      id: json['id'] as String? ?? '',
      mediaId: json['media_id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      averageScore: (json['average_score'] as num?)?.toDouble(),
      fromUserId: json['from_user_id'] as String?,
      fromUsername: json['from_username'] as String?,
      fromDisplayName: json['from_display_name'] as String?,
      fromAvatarUrl: json['from_avatar_url'] as String?,
      message: json['message'] as String?,
    );
  }
}

class HomeGroupWatchingItem {
  final String mediaId;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageLarge;
  final List<WatchingFriend> friends;

  const HomeGroupWatchingItem({
    required this.mediaId,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageLarge,
    this.friends = const [],
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory HomeGroupWatchingItem.fromJson(Map<String, dynamic> json) {
    return HomeGroupWatchingItem(
      mediaId: json['media_id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      friends: (json['friends'] as List<dynamic>?)
              ?.map((e) =>
                  WatchingFriend.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

class WatchingFriend {
  final String userId;
  final String? username;
  final String? displayName;
  final String? avatarUrl;
  final bool isActive;

  const WatchingFriend({
    required this.userId,
    this.username,
    this.displayName,
    this.avatarUrl,
    this.isActive = false,
  });

  factory WatchingFriend.fromJson(Map<String, dynamic> json) {
    return WatchingFriend(
      userId: json['user_id'] as String? ?? '',
      username: json['username'] as String?,
      displayName: json['display_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      isActive: json['is_active'] as bool? ?? false,
    );
  }
}

class HomeAiringSoonItem {
  final String mediaId;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageLarge;
  final int? episodeNumber;
  final String? airingAt;

  const HomeAiringSoonItem({
    required this.mediaId,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageLarge,
    this.episodeNumber,
    this.airingAt,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory HomeAiringSoonItem.fromJson(Map<String, dynamic> json) {
    return HomeAiringSoonItem(
      mediaId: json['media_id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      episodeNumber: json['episode_number'] as int?,
      airingAt: json['airing_at'] as String?,
    );
  }
}

class HomeTrendingItem {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageLarge;
  final double? averageScore;
  final String? format;

  const HomeTrendingItem({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageLarge,
    this.averageScore,
    this.format,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory HomeTrendingItem.fromJson(Map<String, dynamic> json) {
    return HomeTrendingItem(
      id: json['id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      averageScore: (json['average_score'] as num?)?.toDouble(),
      format: json['format'] as String?,
    );
  }
}

// ---------------------------------------------------------------------------
// Genre-based browse section models
// ---------------------------------------------------------------------------

class GenreRailItem {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageLarge;
  final double? averageScore;
  final String? format;

  const GenreRailItem({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageLarge,
    this.averageScore,
    this.format,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory GenreRailItem.fromJson(Map<String, dynamic> json) {
    return GenreRailItem(
      id: json['id'] as String? ?? '',
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      averageScore: (json['average_score'] as num?)?.toDouble(),
      format: json['format'] as String?,
    );
  }
}

class GenreRail {
  final String genreId;
  final String genreName;
  final List<GenreRailItem> items;

  const GenreRail({
    required this.genreId,
    required this.genreName,
    this.items = const [],
  });

  factory GenreRail.fromJson(Map<String, dynamic> json) {
    return GenreRail(
      genreId: json['genre_id'] as String? ?? '',
      genreName: json['genre_name'] as String? ?? '',
      items: (json['items'] as List<dynamic>?)
              ?.map(
                  (e) => GenreRailItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

class MediaTypeSection {
  final String mediaType;
  final String mediaTypeLabel;
  final List<GenreRail> genreRails;

  const MediaTypeSection({
    required this.mediaType,
    required this.mediaTypeLabel,
    this.genreRails = const [],
  });

  factory MediaTypeSection.fromJson(Map<String, dynamic> json) {
    return MediaTypeSection(
      mediaType: json['media_type'] as String? ?? '',
      mediaTypeLabel: json['media_type_label'] as String? ?? '',
      genreRails: (json['genre_rails'] as List<dynamic>?)
              ?.map((e) => GenreRail.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

// ---------------------------------------------------------------------------
// Composite home data
// ---------------------------------------------------------------------------

/// Composite response for GET /api/v1/home
class HomeData {
  final List<HomeSpotlightItem> spotlight;
  final List<HomeContinueItem> continueWatching;
  final List<HomeFriendRecItem> friendRecommendations;
  final List<HomeGroupWatchingItem> groupWatchingNow;
  final List<HomeAiringSoonItem> airingSoon;
  final List<HomeTrendingItem> trendingInGroup;
  final List<MediaTypeSection> mediaTypeSections;

  const HomeData({
    this.spotlight = const [],
    this.continueWatching = const [],
    this.friendRecommendations = const [],
    this.groupWatchingNow = const [],
    this.airingSoon = const [],
    this.trendingInGroup = const [],
    this.mediaTypeSections = const [],
  });

  bool get isEmpty =>
      spotlight.isEmpty &&
      continueWatching.isEmpty &&
      friendRecommendations.isEmpty &&
      groupWatchingNow.isEmpty &&
      airingSoon.isEmpty &&
      trendingInGroup.isEmpty &&
      mediaTypeSections.isEmpty;

  factory HomeData.fromJson(Map<String, dynamic> json) {
    return HomeData(
      spotlight: (json['spotlight'] as List<dynamic>?)
              ?.map((e) =>
                  HomeSpotlightItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      continueWatching: (json['continue_watching'] as List<dynamic>?)
              ?.map((e) =>
                  HomeContinueItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      friendRecommendations:
          (json['friend_recommendations'] as List<dynamic>?)
                  ?.map((e) =>
                      HomeFriendRecItem.fromJson(e as Map<String, dynamic>))
                  .toList() ??
              [],
      groupWatchingNow: (json['group_watching_now'] as List<dynamic>?)
              ?.map((e) =>
                  HomeGroupWatchingItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      airingSoon: (json['airing_soon'] as List<dynamic>?)
              ?.map((e) =>
                  HomeAiringSoonItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      trendingInGroup: (json['trending_in_group'] as List<dynamic>?)
              ?.map((e) =>
                  HomeTrendingItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      mediaTypeSections: (json['media_type_sections'] as List<dynamic>?)
              ?.map((e) =>
                  MediaTypeSection.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}
