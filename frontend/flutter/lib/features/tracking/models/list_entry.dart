/// List entry model from GET /api/v1/lists/me
class ListEntry {
  final String id;
  final String userId;
  final String mediaId;
  final String status;
  final int progress;
  final double? score;
  final String? notes;
  final bool isPrivate;
  final int repeatCount;
  final String? startedAt;
  final String? completedAt;
  final String createdAt;
  final String updatedAt;
  final MediaRef? media;

  const ListEntry({
    required this.id,
    required this.userId,
    required this.mediaId,
    required this.status,
    this.progress = 0,
    this.score,
    this.notes,
    this.isPrivate = false,
    this.repeatCount = 0,
    this.startedAt,
    this.completedAt,
    required this.createdAt,
    required this.updatedAt,
    this.media,
  });

  factory ListEntry.fromJson(Map<String, dynamic> json) {
    return ListEntry(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      mediaId: json['media_id'] as String,
      status: json['status'] as String? ?? 'plan_to_watch',
      progress: json['progress'] as int? ?? 0,
      score: (json['score'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      isPrivate: json['is_private'] as bool? ?? false,
      repeatCount: json['repeat_count'] as int? ?? 0,
      startedAt: json['started_at'] as String?,
      completedAt: json['completed_at'] as String?,
      createdAt: json['created_at'] as String? ?? '',
      updatedAt: json['updated_at'] as String? ?? '',
      media: json['media'] != null
          ? MediaRef.fromJson(json['media'] as Map<String, dynamic>)
          : null,
    );
  }

  String get displayTitle => media?.displayTitle ?? 'Unknown';
  String? get coverImage => media?.coverImageMedium;
  String? get mediaType => media?.mediaType;
  int? get episodeCount => media?.episodeCount;
  int? get chapterCount => media?.chapterCount;
}

class MediaRef {
  final String id;
  final String titleRomaji;
  final String? titleEnglish;
  final String? coverImageMedium;
  final String? coverImageLarge;
  final String mediaType;
  final int? episodeCount;
  final int? chapterCount;

  const MediaRef({
    required this.id,
    required this.titleRomaji,
    this.titleEnglish,
    this.coverImageMedium,
    this.coverImageLarge,
    this.mediaType = 'unknown',
    this.episodeCount,
    this.chapterCount,
  });

  String get displayTitle => titleEnglish ?? titleRomaji;

  factory MediaRef.fromJson(Map<String, dynamic> json) {
    return MediaRef(
      id: json['id'] as String,
      titleRomaji: json['title_romaji'] as String? ?? '',
      titleEnglish: json['title_english'] as String?,
      coverImageMedium: json['cover_image_medium'] as String?,
      coverImageLarge: json['cover_image_large'] as String?,
      mediaType: json['media_type'] as String? ?? 'unknown',
      episodeCount: json['episode_count'] as int?,
      chapterCount: json['chapter_count'] as int?,
    );
  }
}

/// Lightweight stats from GET /api/v1/lists/statistics
class ListStats {
  final int total;
  final int watching;
  final int reading;
  final int completed;
  final int paused;
  final int dropped;
  final int planToWatch;
  final int planToRead;
  final int rewatching;
  final int rereading;

  const ListStats({
    this.total = 0,
    this.watching = 0,
    this.reading = 0,
    this.completed = 0,
    this.paused = 0,
    this.dropped = 0,
    this.planToWatch = 0,
    this.planToRead = 0,
    this.rewatching = 0,
    this.rereading = 0,
  });

  factory ListStats.fromJson(Map<String, dynamic> json) {
    return ListStats(
      total: json['total'] as int? ?? 0,
      watching: json['watching'] as int? ?? 0,
      reading: json['reading'] as int? ?? 0,
      completed: json['completed'] as int? ?? 0,
      paused: json['paused'] as int? ?? 0,
      dropped: json['dropped'] as int? ?? 0,
      planToWatch: json['plan_to_watch'] as int? ?? 0,
      planToRead: json['plan_to_read'] as int? ?? 0,
      rewatching: json['rewatching'] as int? ?? 0,
      rereading: json['rereading'] as int? ?? 0,
    );
  }
}

class HistoryItem {
  final String id;
  final String entryId;
  final String mediaId;
  final String eventType;
  final String? oldStatus;
  final String? newStatus;
  final int? oldProgress;
  final int? newProgress;
  final double? oldScore;
  final double? newScore;
  final String? note;
  final String createdAt;

  const HistoryItem({
    required this.id,
    required this.entryId,
    required this.mediaId,
    required this.eventType,
    this.oldStatus,
    this.newStatus,
    this.oldProgress,
    this.newProgress,
    this.oldScore,
    this.newScore,
    this.note,
    required this.createdAt,
  });

  factory HistoryItem.fromJson(Map<String, dynamic> json) {
    return HistoryItem(
      id: json['id'] as String,
      entryId: json['entry_id'] as String,
      mediaId: json['media_id'] as String,
      eventType: json['event_type'] as String? ?? '',
      oldStatus: json['old_status'] as String?,
      newStatus: json['new_status'] as String?,
      oldProgress: json['old_progress'] as int?,
      newProgress: json['new_progress'] as int?,
      oldScore: (json['old_score'] as num?)?.toDouble(),
      newScore: (json['new_score'] as num?)?.toDouble(),
      note: json['note'] as String?,
      createdAt: json['created_at'] as String? ?? '',
    );
  }

  String get eventDescription {
    switch (eventType) {
      case 'added':
        return 'Added to list';
      case 'removed':
        return 'Removed from list';
      case 'status_changed': {
        final from = oldStatus?.replaceAll('_', ' ') ?? 'none';
        final to = newStatus?.replaceAll('_', ' ') ?? 'none';
        return 'Status: $from → $to';
      }
      case 'progress_updated':
        return 'Progress: ${oldProgress ?? 0} → ${newProgress ?? 0}';
      case 'score_set':
        return 'Score: ${newScore?.toStringAsFixed(1) ?? 'unset'}';
      default:
        return eventType.replaceAll('_', ' ');
    }
  }
}
