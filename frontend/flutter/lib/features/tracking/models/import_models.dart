import 'package:json_annotation/json_annotation.dart';

part 'import_models.g.dart';

@JsonSerializable()
class SyncImportRequest {
  final String? username;
  @JsonKey(name: 'overwrite_existing')
  final bool overwriteExisting;

  const SyncImportRequest({
    this.username,
    this.overwriteExisting = false,
  });

  Map<String, dynamic> toJson() => _$SyncImportRequestToJson(this);
}

@JsonSerializable()
class SyncImportResponse {
  @JsonKey(name: 'job_id')
  final String jobId;
  final String provider;
  final String status;
  @JsonKey(name: 'job_type')
  final String jobType;
  @JsonKey(name: 'started_at')
  final String startedAt;
  final String message;

  const SyncImportResponse({
    required this.jobId,
    required this.provider,
    required this.status,
    required this.jobType,
    required this.startedAt,
    required this.message,
  });

  factory SyncImportResponse.fromJson(Map<String, dynamic> json) =>
      _$SyncImportResponseFromJson(json);
}

@JsonSerializable()
class SyncJobStatusResponse {
  final String id;
  @JsonKey(name: 'job_type')
  final String jobType;
  final String status;
  @JsonKey(name: 'total_items')
  final int? totalItems;
  @JsonKey(name: 'processed_items')
  final int processedItems;
  @JsonKey(name: 'failed_items')
  final int failedItems;
  @JsonKey(name: 'error_log')
  final String? errorLog;
  @JsonKey(name: 'started_at')
  final String startedAt;
  @JsonKey(name: 'completed_at')
  final String? completedAt;

  const SyncJobStatusResponse({
    required this.id,
    required this.jobType,
    required this.status,
    this.totalItems,
    this.processedItems = 0,
    this.failedItems = 0,
    this.errorLog,
    required this.startedAt,
    this.completedAt,
  });

  factory SyncJobStatusResponse.fromJson(Map<String, dynamic> json) =>
      _$SyncJobStatusResponseFromJson(json);

  bool get isRunning => status == 'running';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';
  bool get isPartial => status == 'partial';
}
