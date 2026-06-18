import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/profile/models/user_profile.dart';

// --- Profile fetch provider ---

final profileProvider =
    FutureProvider.autoDispose<UserProfile>((ref) async {
  final dio = ref.read(apiClientProvider);
  final response = await dio.get<dynamic>(ApiEndpoints.usersMe);
  return UserProfile.fromJson(response.data as Map<String, dynamic>);
});

// --- Profile update notifier ---

final profileUpdateProvider =
    AutoDisposeNotifierProvider<ProfileUpdateNotifier, AsyncValue<UserProfile?>>(
  ProfileUpdateNotifier.new,
);

class ProfileUpdateNotifier extends AutoDisposeNotifier<AsyncValue<UserProfile?>> {
  @override
  AsyncValue<UserProfile?> build() => const AsyncData(null);

  Future<UserProfile?> updateProfile(UserUpdate update) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.patch<dynamic>(
        ApiEndpoints.usersMe,
        data: update.toJson(),
      );
      final profile =
          UserProfile.fromJson(response.data as Map<String, dynamic>);
      state = AsyncData(profile);
      ref.invalidate(profileProvider);
      return profile;
    } catch (e) {
      state = AsyncError(e, StackTrace.current);
      return null;
    }
  }
}

// --- Password change notifier ---

final passwordChangeProvider =
    AutoDisposeNotifierProvider<PasswordChangeNotifier, AsyncValue<bool?>>(
  PasswordChangeNotifier.new,
);

class PasswordChangeNotifier extends AutoDisposeNotifier<AsyncValue<bool?>> {
  @override
  AsyncValue<bool?> build() => const AsyncData(null);

  Future<bool?> changePassword(ChangePasswordRequest request) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);
      await dio.post<dynamic>(
        ApiEndpoints.changePassword,
        data: request.toJson(),
      );
      state = const AsyncData(true);
      return true;
    } catch (e) {
      state = AsyncError(e, StackTrace.current);
      return null;
    }
  }
}
