import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/tracking/models/import_models.dart';

/// Provider for initiating a sync import job
final syncImportProvider =
    FutureProvider.family<SyncImportResponse, SyncImportParams>((ref, params) async {
  final dio = ref.read(apiClientProvider);
  final endpoint = params.provider == 'anilist'
      ? ApiEndpoints.syncImportAnilist
      : ApiEndpoints.syncImportMal;

  final response = await dio.post<dynamic>(
    endpoint,
    data: SyncImportRequest(
      username: params.username,
      overwriteExisting: params.overwriteExisting,
    ).toJson(),
  );
  return SyncImportResponse.fromJson(response.data as Map<String, dynamic>);
});

class SyncImportParams {
  final String provider;
  final String? username;
  final bool overwriteExisting;

  const SyncImportParams({
    required this.provider,
    this.username,
    this.overwriteExisting = false,
  });

  @override
  bool operator ==(Object other) =>
      other is SyncImportParams &&
      other.provider == provider &&
      other.username == username &&
      other.overwriteExisting == overwriteExisting;

  @override
  int get hashCode => Object.hash(provider, username, overwriteExisting);
}

/// Provider that polls a sync job status every 3 seconds
final syncJobStatusStreamProvider =
    StreamProvider.family<SyncJobStatusResponse?, String>((ref, jobId) async* {
  final dio = ref.read(apiClientProvider);

  while (true) {
    try {
      final response = await dio.get<dynamic>(
        '${ApiEndpoints.syncJobStatus}/$jobId',
      );
      final status =
          SyncJobStatusResponse.fromJson(response.data as Map<String, dynamic>);
      yield status;

      // Stop polling when job is no longer running
      if (!status.isRunning) {
        return;
      }
    } catch (e) {
      yield null;
      // Wait before retrying on error
      await Future<void>.delayed(const Duration(seconds: 3));
      continue;
    }

    await Future<void>.delayed(const Duration(seconds: 3));
  }
});
