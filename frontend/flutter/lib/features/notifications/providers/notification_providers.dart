import 'package:riverpod/riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/notification_models.dart';

part 'notification_providers.g.dart';

// --- All notifications ---

@riverpod
class AllNotificationsNotifier extends _$AllNotificationsNotifier {
  @override
  Future<NotificationListResponse> build() async {
    return _fetchAll(0);
  }

  Future<NotificationListResponse> _fetchAll(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.notifications,
      queryParameters: {'limit': 50, 'offset': offset},
    );
    return NotificationListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<NotificationListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchAll(data.items.length);
      final combined = NotificationListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

// --- Unread notifications ---

@riverpod
class UnreadNotificationsNotifier extends _$UnreadNotificationsNotifier {
  @override
  Future<NotificationListResponse> build() async {
    return _fetchUnread(0);
  }

  Future<NotificationListResponse> _fetchUnread(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.notifications,
      queryParameters: {'limit': 50, 'offset': offset, 'is_read': false},
    );
    return NotificationListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<NotificationListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchUnread(data.items.length);
      final combined = NotificationListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

// --- Unread count (for badge) ---

@riverpod
Future<int> unreadNotificationCountProvider(Ref ref) async {
  final dio = ref.read(apiClientProvider);
  final response = await dio.get<dynamic>(
    ApiEndpoints.notifications,
    queryParameters: {'limit': 1, 'offset': 0, 'is_read': false},
  );
  final data = NotificationListResponse.fromJson(
    response.data as Map<String, dynamic>,
  );
  return data.total;
}

// --- Mark single notification as read ---

@riverpod
class MarkReadNotifier extends _$MarkReadNotifier {
  @override
  Future<NotificationMarkReadResponse?> build() async => null;

  Future<void> markAsRead(String notificationId) async {
    final dio = ref.read(apiClientProvider);
    await dio.patch<dynamic>(
      ApiEndpoints.notificationsRead,
      data: {'notification_ids': [notificationId]},
    );
    // Invalidate both lists and count
    ref.invalidate(allNotificationsNotifierProvider);
    ref.invalidate(unreadNotificationsNotifierProvider);
    ref.invalidate(unreadNotificationCountProviderProvider);
  }

  Future<void> markAllAsRead() async {
    final dio = ref.read(apiClientProvider);
    await dio.post<dynamic>(
      '${ApiEndpoints.notifications}/mark-all-read',
    );
    ref.invalidate(allNotificationsNotifierProvider);
    ref.invalidate(unreadNotificationsNotifierProvider);
    ref.invalidate(unreadNotificationCountProviderProvider);
  }
}

// --- Delete notification ---

@riverpod
class DeleteNotificationNotifier extends _$DeleteNotificationNotifier {
  @override
  Future<bool?> build() async => null;

  Future<void> delete(String notificationId) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);
      await dio.delete<dynamic>(
        '${ApiEndpoints.notifications}/$notificationId',
      );
      ref.invalidate(allNotificationsNotifierProvider);
      ref.invalidate(unreadNotificationsNotifierProvider);
ref.invalidate(unreadNotificationCountProviderProvider);
      state = const AsyncData(true);
    } catch (e) {
      state = AsyncError(e, StackTrace.current);
    }
  }
}

// --- Notification preferences ---

@riverpod
Future<NotificationPreferences> notificationPreferencesProvider(
  Ref ref,
) async {
  final dio = ref.read(apiClientProvider);
  final response = await dio.get<dynamic>(
    ApiEndpoints.notificationsPreferences,
  );
  return NotificationPreferences.fromJson(
    response.data as Map<String, dynamic>,
  );
}

// --- Update notification preferences ---

@riverpod
class UpdatePreferencesNotifier extends _$UpdatePreferencesNotifier {
  @override
  Future<NotificationPreferences?> build() async => null;

  Future<NotificationPreferences> updatePreferences(
    NotificationPreferencesUpdate updates,
  ) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.patch<dynamic>(
        ApiEndpoints.notificationsPreferences,
        data: updates.toJson(),
      );
      final prefs = NotificationPreferences.fromJson(
        response.data as Map<String, dynamic>,
      );
      ref.invalidate(notificationPreferencesProviderProvider);
      state = AsyncData(prefs);
      return prefs;
    } catch (e) {
      state = AsyncError(e, StackTrace.current);
      rethrow;
    }
  }
}
