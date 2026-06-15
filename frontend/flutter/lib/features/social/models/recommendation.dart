import 'package:json_annotation/json_annotation.dart';

part 'recommendation.g.dart';

@JsonSerializable()
class Recommendation {
  final String id;
  @JsonKey(name: 'from_user_id')
  final String fromUserId;
  @JsonKey(name: 'to_user_id')
  final String toUserId;
  @JsonKey(name: 'media_id')
  final String mediaId;
  final String? message;
  @JsonKey(name: 'is_acknowledged')
  final bool isAcknowledged;
  @JsonKey(name: 'acknowledged_at')
  final String? acknowledgedAt;
  @JsonKey(name: 'created_at')
  final String createdAt;
  @JsonKey(name: 'updated_at')
  final String updatedAt;

  const Recommendation({
    required this.id,
    required this.fromUserId,
    required this.toUserId,
    required this.mediaId,
    this.message,
    this.isAcknowledged = false,
    this.acknowledgedAt,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Recommendation.fromJson(Map<String, dynamic> json) =>
      _$RecommendationFromJson(json);

  Map<String, dynamic> toJson() => _$RecommendationToJson(this);
}

@JsonSerializable()
class CreateRecommendationRequest {
  @JsonKey(name: 'to_user_id')
  final String toUserId;
  @JsonKey(name: 'media_id')
  final String mediaId;
  final String? message;

  const CreateRecommendationRequest({
    required this.toUserId,
    required this.mediaId,
    this.message,
  });

  Map<String, dynamic> toJson() => _$CreateRecommendationRequestToJson(this);
}

@JsonSerializable()
class RecommendationListResponse {
  final List<Recommendation> items;
  final int total;
  final int limit;
  final int offset;

  const RecommendationListResponse({
    this.items = const [],
    this.total = 0,
    this.limit = 50,
    this.offset = 0,
  });

  factory RecommendationListResponse.fromJson(Map<String, dynamic> json) =>
      _$RecommendationListResponseFromJson(json);
}
