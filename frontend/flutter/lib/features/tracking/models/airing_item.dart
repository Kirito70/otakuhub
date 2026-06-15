import 'package:json_annotation/json_annotation.dart';

part 'airing_item.g.dart';

@JsonSerializable()
class AiringEpisodeItem {
  final String id;
  final String mediaId;
  final String mediaTitle;
  final String? mediaCover;
  final String? mediaType;
  final int episodeNumber;
  final String? title;
  final String? airDate;
  final int? durationMinutes;

  const AiringEpisodeItem({
    required this.id,
    required this.mediaId,
    required this.mediaTitle,
    this.mediaCover,
    this.mediaType,
    required this.episodeNumber,
    this.title,
    this.airDate,
    this.durationMinutes,
  });

  factory AiringEpisodeItem.fromJson(Map<String, dynamic> json) =>
      _$AiringEpisodeItemFromJson(json);

  Map<String, dynamic> toJson() => _$AiringEpisodeItemToJson(this);
}

@JsonSerializable()
class AiringResponse {
  final List<AiringEpisodeItem> items;
  final int total;
  final int limit;
  final int offset;

  const AiringResponse({
    this.items = const [],
    this.total = 0,
    this.limit = 20,
    this.offset = 0,
  });

  factory AiringResponse.fromJson(Map<String, dynamic> json) =>
      _$AiringResponseFromJson(json);
}
