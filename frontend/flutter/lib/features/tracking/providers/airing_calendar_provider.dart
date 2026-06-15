import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/api/api_client.dart';
import 'package:otakuhub/core/api/api_endpoints.dart';
import 'package:otakuhub/features/tracking/models/airing_item.dart';

/// Provider for the airing schedule from GET /api/v1/media/airing
final airingScheduleProvider = FutureProvider<AiringResponse>((ref) async {
  final dio = ref.read(apiClientProvider);
  final response = await dio.get<dynamic>(
    ApiEndpoints.mediaAiring,
    queryParameters: <String, dynamic>{
      'limit': 50,
      'offset': 0,
    },
  );
  return AiringResponse.fromJson(response.data as Map<String, dynamic>);
});
