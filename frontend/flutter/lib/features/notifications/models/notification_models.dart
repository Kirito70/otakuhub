import 'package:freezed_annotation/freezed_annotation.dart';

part 'notification_models.freezed.dart';
part 'notification_models.g.dart';

// --- Single notification item ---

@freezed
class NotificationItem with _$NotificationItem {
  const factory NotificationItem({
    required String id,
    @JsonKey(name: 'user_id') required String userId,
    required String type,
    required String title,
    String? body,
    @JsonKey(name: 'action_url') String? actionUrl,
    @JsonKey(name: 'related_media_id') String? relatedMediaId,
    @JsonKey(name: 'related_user_id') String? relatedUserId,
    @JsonKey(name: 'is_read') required bool isRead,
    @JsonKey(name: 'read_at') DateTime? readAt,
    @JsonKey(name: 'sent_at') DateTime? sentAt,
    @JsonKey(name: 'created_at') required DateTime createdAt,
  }) = _NotificationItem;

  factory NotificationItem.fromJson(Map<String, dynamic> json) =>
      _$NotificationItemFromJson(json);
}

// --- Paginated list response ---

@freezed
class NotificationListResponse with _$NotificationListResponse {
  const factory NotificationListResponse({
    required List<NotificationItem> items,
    required int total,
    required int limit,
    required int offset,
  }) = _NotificationListResponse;

  factory NotificationListResponse.fromJson(Map<String, dynamic> json) =>
      _$NotificationListResponseFromJson(json);
}

// --- Mark-read response ---

@freezed
class NotificationMarkReadResponse with _$NotificationMarkReadResponse {
  const factory NotificationMarkReadResponse({
    @JsonKey(name: 'updated_count') required int updatedCount,
  }) = _NotificationMarkReadResponse;

  factory NotificationMarkReadResponse.fromJson(Map<String, dynamic> json) =>
      _$NotificationMarkReadResponseFromJson(json);
}

// --- Preferences ---

@freezed
class NotificationPreferences with _$NotificationPreferences {
  const factory NotificationPreferences({
    @JsonKey(name: 'user_id') required String userId,
    @JsonKey(name: 'new_episode') required bool newEpisode,
    @JsonKey(name: 'new_chapter') required bool newChapter,
    @JsonKey(name: 'friend_activity') required bool friendActivity,
    required bool recommendations,
    @JsonKey(name: 'watch_party_invite') required bool watchPartyInvite,
    @JsonKey(name: 'watch_party_reminder') required bool watchPartyReminder,
    @JsonKey(name: 'discord_webhook') String? discordWebhook,
    @JsonKey(name: 'telegram_chat_id') String? telegramChatId,
    @JsonKey(name: 'email_enabled') required bool emailEnabled,
    @JsonKey(name: 'push_enabled') required bool pushEnabled,
    @JsonKey(name: 'updated_at') required DateTime updatedAt,
  }) = _NotificationPreferences;

  factory NotificationPreferences.fromJson(Map<String, dynamic> json) =>
      _$NotificationPreferencesFromJson(json);
}

// --- Preferences update request ---

@freezed
class NotificationPreferencesUpdate with _$NotificationPreferencesUpdate {
  const factory NotificationPreferencesUpdate({
    @JsonKey(name: 'new_episode') bool? newEpisode,
    @JsonKey(name: 'new_chapter') bool? newChapter,
    @JsonKey(name: 'friend_activity') bool? friendActivity,
    bool? recommendations,
    @JsonKey(name: 'watch_party_invite') bool? watchPartyInvite,
    @JsonKey(name: 'watch_party_reminder') bool? watchPartyReminder,
    @JsonKey(name: 'discord_webhook') String? discordWebhook,
    @JsonKey(name: 'telegram_chat_id') String? telegramChatId,
    @JsonKey(name: 'email_enabled') bool? emailEnabled,
    @JsonKey(name: 'push_enabled') bool? pushEnabled,
  }) = _NotificationPreferencesUpdate;

  factory NotificationPreferencesUpdate.fromJson(Map<String, dynamic> json) =>
      _$NotificationPreferencesUpdateFromJson(json);
}
