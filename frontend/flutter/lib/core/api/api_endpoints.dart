class ApiEndpoints {
  ApiEndpoints._();

  static const String baseUrl = 'http://localhost:8000';

  // Auth
  static const String login = '/api/v1/auth/login';
  static const String register = '/api/v1/auth/register';
  static const String refresh = '/api/v1/auth/refresh';
  static const String logout = '/api/v1/auth/logout';

  // Setup
  static const String setupStatus = '/api/v1/setup/status';
  static const String setupBootstrap = '/api/v1/setup/bootstrap-admin';

  // Users
  static const String usersMe = '/api/v1/users/me';
  static const String usersProfile = '/api/v1/users'; // + /{username}/profile

  // Media
  static const String mediaSearch = '/api/v1/media/search';
  static const String mediaTrending = '/api/v1/media/trending';
  static const String mediaPopular = '/api/v1/media/popular';
  static const String mediaSeasonal = '/api/v1/media/seasonal';
  static const String mediaDetail = '/api/v1/media'; // + /{id}
  static const String mediaRelations = '/api/v1/media'; // + /{id}/relations
  static const String mediaEpisodes = '/api/v1/media/episodes'; // + /{id}
  static const String mediaChapters = '/api/v1/media/chapters'; // + /{id}
  static const String mediaGenres = '/api/v1/media/genres';
  static const String mediaSources = '/api/v1/media/sources'; // + /{id}
  static const String mediaEpisodeSources = '/api/v1/media/episodes/sources'; // + /{id}
  static const String mediaAiring = '/api/v1/media/airing';

  // Lists / Tracking
  static const String listsMe = '/api/v1/lists/me';
  static const String listsEntry = '/api/v1/lists'; // + /{media_id}
  static const String listsHistory = '/api/v1/lists/me/history';
  static const String listsStats = '/api/v1/lists/statistics';
  static const String listsCustom = '/api/v1/lists/custom';

  // Social
  static const String socialFeed = '/api/v1/social/feed';
  static const String socialRecommend = '/api/v1/social/recommend';
  static const String socialRecInbox = '/api/v1/social/recommendations/inbox';
  static const String socialDiscussions = '/api/v1/social/discussions';

  // Watch Party
  static const String watchParty = '/api/v1/watchparty';
  static const String watchPartyRsvp = '/api/v1/watchparty'; // + /{id}/rsvp

  // Notifications
  static const String notifications = '/api/v1/notifications';
  static const String notificationsRead = '/api/v1/notifications/read';
  static const String notificationsPreferences = '/api/v1/notifications/preferences';

  // Sync
  static const String syncImportAnilist = '/api/v1/sync/import/anilist';
  static const String syncImportMal = '/api/v1/sync/import/mal';
  static const String syncJobStatus = '/api/v1/sync/jobs'; // + /{job_id}

  // Admin
  static const String adminSourceMappings = '/api/v1/admin/source-mappings';
  static const String adminUsers = '/api/v1/admin/users';
}
