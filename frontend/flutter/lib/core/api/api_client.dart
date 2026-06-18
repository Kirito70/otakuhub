import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/auth/storage_service.dart';
import 'package:otakuhub/core/auth/auth_provider.dart';

final apiClientProvider = Provider<Dio>((ref) {
  final dio = Dio(BaseOptions(
    baseUrl: 'http://localhost:8000',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  dio.interceptors.add(AuthInterceptor(ref));
  dio.interceptors.add(LogInterceptor(
    requestBody: true,
    responseBody: true,
    logPrint: (o) => print('[DIO] $o'),
  ));

  return dio;
});

class AuthInterceptor extends Interceptor {
  final Ref _ref;

  AuthInterceptor(this._ref);

  /// Tracks whether we are already in a refresh flow to prevent re-entrant loops.
  bool _isRefreshing = false;

  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Don't attach the (possibly expired) access token to refresh requests.
    // The refresh endpoint only needs the refresh token in the request body.
    if (options.path.contains('/auth/refresh')) {
      handler.next(options);
      return;
    }
    final storage = _ref.read(storageServiceProvider);
    final token = await storage.getAccessToken();
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  void onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    // Only handle 401 errors; never recursively handle errors from the
    // refresh request itself.
    if (err.response?.statusCode != 401 || _isRefreshing) {
      handler.next(err);
      return;
    }

    _isRefreshing = true;
    try {
      final authNotifier = _ref.read(authProvider.notifier);
      final success = await authNotifier.refreshToken();

      if (success) {
        final storage = _ref.read(storageServiceProvider);
        final newToken = await storage.getAccessToken();
        if (newToken != null) {
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
          // Use a fresh Dio without interceptors to avoid re-triggering this flow.
          final cleanDio = Dio(BaseOptions());
          final response = await cleanDio.fetch<dynamic>(err.requestOptions);
          handler.resolve(response);
          _isRefreshing = false;
          return;
        }
      }

      await authNotifier.logoutSilent();
    } catch (_) {
      await _ref.read(authProvider.notifier).logoutSilent();
    }
    _isRefreshing = false;
    handler.next(err);
  }
}
