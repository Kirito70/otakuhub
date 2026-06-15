import 'package:freezed_annotation/freezed_annotation.dart';

part 'watch_party.freezed.dart';
part 'watch_party.g.dart';

// --- List item (WatchPartyResponse) ---

@freezed
class WatchParty with _$WatchParty {
  const factory WatchParty({
    required String id,
    @JsonKey(name: 'group_id') required String groupId,
    @JsonKey(name: 'host_user_id') required String hostUserId,
    @JsonKey(name: 'media_id') required String mediaId,
    @JsonKey(name: 'episode_number') int? episodeNumber,
    String? title,
    @JsonKey(name: 'scheduled_at') required DateTime scheduledAt,
    required String status,
    @JsonKey(name: 'stream_url') String? streamUrl,
    @JsonKey(name: 'sync_url') String? syncUrl,
    String? notes,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
  }) = _WatchParty;

  factory WatchParty.fromJson(Map<String, dynamic> json) =>
      _$WatchPartyFromJson(json);
}

// --- Detail (WatchPartyDetailResponse) ---

@freezed
class WatchPartyDetail with _$WatchPartyDetail {
  const factory WatchPartyDetail({
    required String id,
    @JsonKey(name: 'group_id') required String groupId,
    @JsonKey(name: 'host_user_id') required String hostUserId,
    @JsonKey(name: 'host_username') String? hostUsername,
    @JsonKey(name: 'host_display_name') String? hostDisplayName,
    @JsonKey(name: 'media_id') required String mediaId,
    @JsonKey(name: 'media_title') String? mediaTitle,
    @JsonKey(name: 'media_cover') String? mediaCover,
    @JsonKey(name: 'episode_number') int? episodeNumber,
    String? title,
    @JsonKey(name: 'scheduled_at') required DateTime scheduledAt,
    required String status,
    @JsonKey(name: 'stream_url') String? streamUrl,
    @JsonKey(name: 'sync_url') String? syncUrl,
    String? notes,
    @JsonKey(name: 'created_at') required DateTime createdAt,
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
    @JsonKey(name: 'rsvp_summary')
    @Default(<String, int>{})
    Map<String, int> rsvpSummary,
    @JsonKey(name: 'attendee_count') @Default(0) int attendeeCount,
  }) = _WatchPartyDetail;

  factory WatchPartyDetail.fromJson(Map<String, dynamic> json) =>
      _$WatchPartyDetailFromJson(json);
}

// --- Paginated list response ---

@freezed
class WatchPartyListResponse with _$WatchPartyListResponse {
  const factory WatchPartyListResponse({
    required List<WatchParty> items,
    required int total,
    required int limit,
    required int offset,
  }) = _WatchPartyListResponse;

  factory WatchPartyListResponse.fromJson(Map<String, dynamic> json) =>
      _$WatchPartyListResponseFromJson(json);
}

// --- RSVP ---

@freezed
class WatchPartyRsvp with _$WatchPartyRsvp {
  const factory WatchPartyRsvp({
    @JsonKey(name: 'party_id') required String partyId,
    @JsonKey(name: 'user_id') required String userId,
    required String status,
    @JsonKey(name: 'responded_at') DateTime? respondedAt,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _WatchPartyRsvp;

  factory WatchPartyRsvp.fromJson(Map<String, dynamic> json) =>
      _$WatchPartyRsvpFromJson(json);
}

@freezed
class WatchPartyRsvpListResponse with _$WatchPartyRsvpListResponse {
  const factory WatchPartyRsvpListResponse({
    required List<WatchPartyRsvp> items,
    required int total,
  }) = _WatchPartyRsvpListResponse;

  factory WatchPartyRsvpListResponse.fromJson(Map<String, dynamic> json) =>
      _$WatchPartyRsvpListResponseFromJson(json);
}

// --- Create request ---

@freezed
class WatchPartyCreateRequest with _$WatchPartyCreateRequest {
  const factory WatchPartyCreateRequest({
    @JsonKey(name: 'group_id') required String groupId,
    @JsonKey(name: 'media_id') required String mediaId,
    @JsonKey(name: 'scheduled_at') required DateTime scheduledAt,
    String? title,
    @JsonKey(name: 'episode_number') int? episodeNumber,
    @JsonKey(name: 'stream_url') String? streamUrl,
    @JsonKey(name: 'sync_url') String? syncUrl,
    String? notes,
  }) = _WatchPartyCreateRequest;

  factory WatchPartyCreateRequest.fromJson(Map<String, dynamic> json) =>
      _$WatchPartyCreateRequestFromJson(json);
}

// --- RSVP request ---

@freezed
class WatchPartyRsvpRequest with _$WatchPartyRsvpRequest {
  const factory WatchPartyRsvpRequest({
    required String status,
  }) = _WatchPartyRsvpRequest;

  factory WatchPartyRsvpRequest.fromJson(Map<String, dynamic> json) =>
      _$WatchPartyRsvpRequestFromJson(json);
}
