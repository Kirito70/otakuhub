class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final dynamic data;

  ApiException(this.message, {this.statusCode, this.data});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class UnauthorizedException extends ApiException {
  UnauthorizedException([String message = 'Unauthorized'])
      : super(message, statusCode: 401);
}

class NotFoundException extends ApiException {
  NotFoundException([String message = 'Not found'])
      : super(message, statusCode: 404);
}

class ValidationException extends ApiException {
  final Map<String, List<String>>? errors;

  ValidationException(
    String message, {
    this.errors,
  }) : super(message, statusCode: 422);

  factory ValidationException.fromResponse(Map<String, dynamic> data) {
    final detail = data['detail'];
    if (detail is List) {
      final errors = <String, List<String>>{};
      for (final err in detail) {
        final loc = (err['loc'] as List?)?.skip(1).join('.') ?? 'unknown';
        final msg = err['msg'] as String? ?? 'Invalid value';
        errors.putIfAbsent(loc, () => []).add(msg);
      }
      return ValidationException('Validation failed', errors: errors);
    }
    return ValidationException(detail?.toString() ?? 'Validation failed');
  }
}

class ServerException extends ApiException {
  ServerException([String message = 'Internal server error'])
      : super(message, statusCode: 500);
}

class NetworkException extends ApiException {
  NetworkException([String message = 'Network error'])
      : super(message);
}
