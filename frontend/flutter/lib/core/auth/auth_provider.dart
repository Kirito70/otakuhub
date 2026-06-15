import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/core/auth/storage_service.dart';

part 'auth_provider.freezed.dart';
part 'auth_provider.g.dart';

// --- Models ---

@freezed
class AuthState with _$AuthState {
  const factory AuthState({
    @Default(false) bool isAuthenticated,
    @Default(false) bool isLoading,
    @Default(false) bool isSetupRequired,
    String? error,
    User? user,
  }) = _AuthState;
}

@freezed
class User with _$User {
  const factory User({
    required String id,
    required String username,
    String? displayName,
    String? email,
    String? avatarUrl,
    String? bio,
    @Default(false) bool isAdmin,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

@freezed
class LoginRequest with _$LoginRequest {
  const factory LoginRequest({
    required String username,
    required String password,
  }) = _LoginRequest;

  factory LoginRequest.fromJson(Map<String, dynamic> json) =>
      _$LoginRequestFromJson(json);
}

@freezed
class RegisterRequest with _$RegisterRequest {
  const factory RegisterRequest({
    required String username,
    required String email,
    required String password,
  }) = _RegisterRequest;

  factory RegisterRequest.fromJson(Map<String, dynamic> json) =>
      _$RegisterRequestFromJson(json);
}

@freezed
class TokenResponse with _$TokenResponse {
  const factory TokenResponse({
    required String accessToken,
    required String refreshToken,
    @Default('bearer') String tokenType,
  }) = _TokenResponse;

  factory TokenResponse.fromJson(Map<String, dynamic> json) =>
      _$TokenResponseFromJson(json);
}

// --- Provider ---

final authProvider = NotifierProvider<AuthNotifier, AuthState>(
  AuthNotifier.new,
);

class AuthNotifier extends Notifier<AuthState> {
  @override
  AuthState build() {
    _hydrate();
    return const AuthState();
  }

  Dio get _dio => ref.read(apiClientProvider);
  StorageService get _storage => ref.read(storageServiceProvider);

  Future<void> _hydrate() async {
    final token = await _storage.getAccessToken();
    if (token != null) {
      final username = await _storage.getUsername();
      final userId = await _storage.getUserId();
      state = AuthState(
        isAuthenticated: true,
        user: userId != null
            ? User(id: userId, username: username ?? '')
            : null,
      );
    }
  }

  Future<void> login(String username, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.login,
        data: LoginRequest(username: username, password: password).toJson(),
      );

      final tokenResponse = TokenResponse.fromJson(response.data!);

      // Fetch user profile
      final userResponse = await _dio.get<Map<String, dynamic>>(ApiEndpoints.usersMe);
      final user = User.fromJson(userResponse.data!);

      // Persist tokens
      await _storage.saveAccessToken(tokenResponse.accessToken);
      await _storage.saveRefreshToken(tokenResponse.refreshToken);
      await _storage.saveUserId(user.id);
      await _storage.saveUsername(user.username);

      state = AuthState(isAuthenticated: true, user: user);
    } on DioException catch (e) {
      final message = _mapDioError(e);
      state = state.copyWith(isLoading: false, error: message);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'An unexpected error occurred',
      );
    }
  }

  Future<void> register(String username, String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.register,
        data: RegisterRequest(
          username: username,
          email: email,
          password: password,
        ).toJson(),
      );

      final tokenResponse = TokenResponse.fromJson(response.data!);

      // Fetch user profile
      final userResponse = await _dio.get<Map<String, dynamic>>(ApiEndpoints.usersMe);
      final user = User.fromJson(userResponse.data!);

      await _storage.saveAccessToken(tokenResponse.accessToken);
      await _storage.saveRefreshToken(tokenResponse.refreshToken);
      await _storage.saveUserId(user.id);
      await _storage.saveUsername(user.username);

      state = AuthState(isAuthenticated: true, user: user);
    } on DioException catch (e) {
      final message = _mapDioError(e);
      state = state.copyWith(isLoading: false, error: message);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'An unexpected error occurred',
      );
    }
  }

  Future<bool> refreshToken() async {
    try {
      final refreshToken = await _storage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.refresh,
        data: {'refresh_token': refreshToken},
      );

      final tokenResponse = TokenResponse.fromJson(response.data!);
      await _storage.saveAccessToken(tokenResponse.accessToken);
      await _storage.saveRefreshToken(tokenResponse.refreshToken);

      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> logout() async {
    try {
      await _dio.post<void>(ApiEndpoints.logout);
    } catch (_) {
      // Best-effort logout
    }
    await _storage.clearAll();
    state = const AuthState();
  }

  Future<bool> checkSetupStatus() async {
    try {
      final response = await _dio.get<Map<String, dynamic>>(ApiEndpoints.setupStatus);
      final needsSetup = response.data!['needs_setup'] as bool? ?? true;
      state = state.copyWith(isSetupRequired: needsSetup);
      return needsSetup;
    } catch (_) {
      return true;
    }
  }

  Future<void> bootstrapAdmin({
    required String username,
    required String email,
    required String password,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    try {
      final response = await _dio.post<Map<String, dynamic>>(
        ApiEndpoints.setupBootstrap,
        data: {
          'username': username,
          'email': email,
          'password': password,
        },
      );

      final tokenResponse = TokenResponse.fromJson(response.data!);

      final userResponse = await _dio.get<Map<String, dynamic>>(ApiEndpoints.usersMe);
      final user = User.fromJson(userResponse.data!);

      await _storage.saveAccessToken(tokenResponse.accessToken);
      await _storage.saveRefreshToken(tokenResponse.refreshToken);
      await _storage.saveUserId(user.id);
      await _storage.saveUsername(user.username);

      state = AuthState(isAuthenticated: true, user: user, isSetupRequired: false);
    } on DioException catch (e) {
      final message = _mapDioError(e);
      state = state.copyWith(isLoading: false, error: message);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'An unexpected error occurred',
      );
    }
  }

  void clearError() {
    state = state.copyWith(error: null);
  }

  String _mapDioError(DioException e) {
    switch (e.response?.statusCode) {
      case 401:
        return 'Invalid username or password';
      case 409:
        return 'User already exists';
      case 422:
        final data = e.response?.data;
        if (data is Map<String, dynamic>) {
          final detail = data['detail'];
          if (detail is List && detail.isNotEmpty) {
            return detail[0]['msg']?.toString() ?? 'Validation error';
          }
          return detail?.toString() ?? 'Validation error';
        }
        return 'Invalid input';
      case 429:
        return 'Too many attempts. Please try again later.';
      default:
        if (e.type == DioExceptionType.connectionTimeout ||
            e.type == DioExceptionType.receiveTimeout) {
          return 'Connection timed out. Please try again.';
        }
        if (e.type == DioExceptionType.connectionError) {
          return 'Could not connect to server. Please check your connection.';
        }
        return e.response?.data?['detail']?.toString() ??
            'An error occurred. Please try again.';
    }
  }
}
