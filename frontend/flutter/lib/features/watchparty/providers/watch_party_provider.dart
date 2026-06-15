import 'package:riverpod/riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

import '../../../core/api/api_client.dart';
import '../../../core/api/api_endpoints.dart';
import '../models/watch_party.dart';

part 'watch_party_provider.g.dart';

// --- Upcoming parties ---

@riverpod
class UpcomingPartiesNotifier extends _$UpcomingPartiesNotifier {
  @override
  Future<WatchPartyListResponse> build() async {
    return _fetchUpcoming(0);
  }

  Future<WatchPartyListResponse> _fetchUpcoming(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.watchParty,
      queryParameters: {'limit': 50, 'offset': offset},
    );
    return WatchPartyListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<WatchPartyListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchUpcoming(data.items.length);
      final combined = WatchPartyListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

// --- Past parties ---

@riverpod
class PastPartiesNotifier extends _$PastPartiesNotifier {
  @override
  Future<WatchPartyListResponse> build() async {
    return _fetchPast(0);
  }

  Future<WatchPartyListResponse> _fetchPast(int offset) async {
    final dio = ref.read(apiClientProvider);
    final response = await dio.get<dynamic>(
      ApiEndpoints.watchPartyPast,
      queryParameters: {'limit': 50, 'offset': offset},
    );
    return WatchPartyListResponse.fromJson(
      response.data as Map<String, dynamic>,
    );
  }

  Future<void> loadMore() async {
    final current = state;
    if (current is AsyncData<WatchPartyListResponse>) {
      final data = current.value;
      if (data.items.length >= data.total) return;
      final more = await _fetchPast(data.items.length);
      final combined = WatchPartyListResponse(
        items: [...data.items, ...more.items],
        total: more.total,
        limit: more.limit,
        offset: data.items.length,
      );
      state = AsyncData(combined);
    }
  }
}

// --- Party detail ---

@riverpod
Future<WatchPartyDetail> partyDetailProvider(
  Ref ref,
  String partyId,
) async {
  final dio = ref.read(apiClientProvider);
  final response = await dio.get<dynamic>(
    '${ApiEndpoints.watchParty}/$partyId',
  );
  return WatchPartyDetail.fromJson(response.data as Map<String, dynamic>);
}

// --- RSVPs ---

@riverpod
Future<WatchPartyRsvpListResponse> partyRsvpsProvider(
  Ref ref,
  String partyId,
) async {
  final dio = ref.read(apiClientProvider);
  final response = await dio.get<dynamic>(
    '${ApiEndpoints.watchParty}/$partyId/rsvps',
  );
  return WatchPartyRsvpListResponse.fromJson(
    response.data as Map<String, dynamic>,
  );
}

// --- Create party ---

@riverpod
class CreatePartyNotifier extends _$CreatePartyNotifier {
  @override
  Future<WatchParty?> build() async => null;

  Future<WatchParty> create(WatchPartyCreateRequest request) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.post<dynamic>(
        ApiEndpoints.watchParty,
        data: request.toJson(),
      );
      final party = WatchParty.fromJson(response.data as Map<String, dynamic>);

      // Invalidate the upcoming list so it refreshes
      ref.invalidate(upcomingPartiesNotifierProvider);

      state = AsyncData(party);
      return party;
    } catch (e) {
      state = AsyncError(e, StackTrace.current);
      rethrow;
    }
  }
}

// --- RSVP action ---

@riverpod
class RsvpNotifier extends _$RsvpNotifier {
  @override
  Future<WatchPartyRsvp?> build() async => null;

  Future<WatchPartyRsvp> rsvp({
    required String partyId,
    required String status,
  }) async {
    state = const AsyncLoading();
    try {
      final dio = ref.read(apiClientProvider);
      final response = await dio.post<dynamic>(
        '${ApiEndpoints.watchParty}/$partyId/rsvp',
        data: WatchPartyRsvpRequest(status: status).toJson(),
      );
      final rsvpResult = WatchPartyRsvp.fromJson(
        response.data as Map<String, dynamic>,
      );

      // Invalidate both upcoming list and details
      ref.invalidate(upcomingPartiesNotifierProvider);
      ref.invalidate(partyDetailProviderProvider(partyId));
      ref.invalidate(partyRsvpsProviderProvider(partyId));

      state = AsyncData(rsvpResult);
      return rsvpResult;
    } catch (e) {
      state = AsyncError(e, StackTrace.current);
      rethrow;
    }
  }
}
