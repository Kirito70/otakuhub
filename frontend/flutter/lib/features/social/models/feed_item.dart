import 'package:json_annotation/json_annotation.dart';

part 'feed_item.g.dart';

@JsonSerializable()
class FeedActivityItem {
  final String id;
  @JsonKey(name: 'entry_id')
  final String entryId;
  @JsonKey(name: 'user_id')
  final String userId;
  @JsonKey(name: 'media_id')
  final String mediaId;
  @JsonKey(name: 'event_type')
  final String eventType;
  @JsonKey(name: 'old_status')
  final String? oldStatus;
  @JsonKey(name: 'new_status')
  final String? newStatus;
  @JsonKey(name: 'old_progress')
  final int? oldProgress;
  @JsonKey(name: 'new_progress')
  final int? newProgress;
  @JsonKey(name: 'old_score')
  final double? oldScore;
  @JsonKey(name: 'new_score')
  final double? newScore;
  final String? note;
  @JsonKey(name: 'created_at')
  final String createdAt;

  const FeedActivityItem({
    required this.id,
    required this.entryId,
    required this.userId,
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

  factory FeedActivityItem.fromJson(Map<String, dynamic> json) =>
      _$FeedActivityItemFromJson(json);

  Map<String, dynamic> toJson() => _$FeedActivityItemToJson(this);
}

@JsonSerializable()
class FeedResponse {
  final List<FeedActivityItem> items;
  final int total;
  final int limit;
  final int offset;

  const FeedResponse({
    this.items = const [],
    this.total = 0,
    this.limit = 50,
    this.offset = 0,
  });

  factory FeedResponse.fromJson(Map<String, dynamic> json) =>
      _$FeedResponseFromJson(json);
}
