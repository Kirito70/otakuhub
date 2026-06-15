import 'package:json_annotation/json_annotation.dart';

part 'discussion.g.dart';

@JsonSerializable()
class Discussion {
  final String id;
  @JsonKey(name: 'media_id')
  final String mediaId;
  @JsonKey(name: 'group_id')
  final String groupId;
  @JsonKey(name: 'user_id')
  final String userId;
  final String? title;
  final String body;
  @JsonKey(name: 'has_spoilers')
  final bool hasSpoilers;
  @JsonKey(name: 'episode_number')
  final int? episodeNumber;
  @JsonKey(name: 'chapter_number')
  final double? chapterNumber;
  @JsonKey(name: 'created_at')
  final String createdAt;
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  const Discussion({
    required this.id,
    required this.mediaId,
    required this.groupId,
    required this.userId,
    this.title,
    required this.body,
    this.hasSpoilers = false,
    this.episodeNumber,
    this.chapterNumber,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Discussion.fromJson(Map<String, dynamic> json) =>
      _$DiscussionFromJson(json);

  Map<String, dynamic> toJson() => _$DiscussionToJson(this);
}

@JsonSerializable()
class CreateDiscussionRequest {
  @JsonKey(name: 'media_id')
  final String mediaId;
  @JsonKey(name: 'group_id')
  final String groupId;
  final String? title;
  final String body;
  @JsonKey(name: 'has_spoilers')
  final bool hasSpoilers;
  @JsonKey(name: 'episode_number')
  final int? episodeNumber;
  @JsonKey(name: 'chapter_number')
  final double? chapterNumber;

  const CreateDiscussionRequest({
    required this.mediaId,
    required this.groupId,
    this.title,
    required this.body,
    this.hasSpoilers = false,
    this.episodeNumber,
    this.chapterNumber,
  });

  Map<String, dynamic> toJson() => _$CreateDiscussionRequestToJson(this);
}

@JsonSerializable()
class DiscussionListResponse {
  final List<Discussion> items;
  final int total;
  final int limit;
  final int offset;

  const DiscussionListResponse({
    this.items = const [],
    this.total = 0,
    this.limit = 50,
    this.offset = 0,
  });

  factory DiscussionListResponse.fromJson(Map<String, dynamic> json) =>
      _$DiscussionListResponseFromJson(json);
}

@JsonSerializable()
class DiscussionReply {
  final String id;
  @JsonKey(name: 'discussion_id')
  final String discussionId;
  @JsonKey(name: 'user_id')
  final String userId;
  @JsonKey(name: 'parent_reply_id')
  final String? parentReplyId;
  final String body;
  @JsonKey(name: 'has_spoilers')
  final bool hasSpoilers;
  @JsonKey(name: 'created_at')
  final String createdAt;
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  const DiscussionReply({
    required this.id,
    required this.discussionId,
    required this.userId,
    this.parentReplyId,
    required this.body,
    this.hasSpoilers = false,
    required this.createdAt,
    required this.updatedAt,
  });

  factory DiscussionReply.fromJson(Map<String, dynamic> json) =>
      _$DiscussionReplyFromJson(json);

  Map<String, dynamic> toJson() => _$DiscussionReplyToJson(this);
}

@JsonSerializable()
class CreateReplyRequest {
  final String body;
  @JsonKey(name: 'has_spoilers')
  final bool hasSpoilers;
  @JsonKey(name: 'parent_reply_id')
  final String? parentReplyId;

  const CreateReplyRequest({
    required this.body,
    this.hasSpoilers = false,
    this.parentReplyId,
  });

  Map<String, dynamic> toJson() => _$CreateReplyRequestToJson(this);
}

@JsonSerializable()
class ReplyListResponse {
  final List<DiscussionReply> items;
  final int total;
  final int limit;
  final int offset;

  const ReplyListResponse({
    this.items = const [],
    this.total = 0,
    this.limit = 50,
    this.offset = 0,
  });

  factory ReplyListResponse.fromJson(Map<String, dynamic> json) =>
      _$ReplyListResponseFromJson(json);
}
