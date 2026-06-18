import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'package:otakuhub/core/auth/auth_provider.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/widgets/adaptive_scaffold.dart';

// Screens
import 'package:otakuhub/features/auth/screens/login_screen.dart';
import 'package:otakuhub/features/auth/screens/register_screen.dart';
import 'package:otakuhub/features/auth/screens/setup_screen.dart';
import 'package:otakuhub/features/discover/screens/discover_screen.dart';
import 'package:otakuhub/features/discover/screens/search_results_screen.dart';
import 'package:otakuhub/features/media_detail/screens/media_detail_screen.dart';
import 'package:otakuhub/features/tracking/screens/my_list_screen.dart';
import 'package:otakuhub/features/tracking/screens/airing_calendar_screen.dart';
import 'package:otakuhub/features/tracking/screens/import_list_screen.dart';
import 'package:otakuhub/features/social/screens/feed_screen.dart';
import 'package:otakuhub/features/social/screens/recommendations_screen.dart';
import 'package:otakuhub/features/social/screens/discussion_list_screen.dart';
import 'package:otakuhub/features/social/screens/discussion_detail_screen.dart';
import 'package:otakuhub/features/watchparty/screens/watch_party_screen.dart';
import 'package:otakuhub/features/notifications/screens/notifications_screen.dart';
import 'package:otakuhub/features/notifications/screens/notification_preferences_screen.dart';
import 'package:otakuhub/features/profile/screens/profile_screen.dart';
import 'package:otakuhub/features/profile/screens/edit_profile_screen.dart';
import 'package:otakuhub/features/profile/screens/account_security_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  // Watch the auth refresh notifier so GoRouter re-evaluates on auth changes.
  // We don't watch authProvider directly — that would recreate GoRouter on every
  // auth state change (losing navigation history). Instead we use refreshListenable
  // which tells GoRouter to re-run the redirect callback in-place.
  final refreshListenable = ref.watch(authRefreshNotifierProvider);

  return GoRouter(
    initialLocation: '/discover',
    debugLogDiagnostics: true,
    refreshListenable: refreshListenable,

    redirect: (context, state) {
      final authState = ref.read(authProvider);
      final isLoggedIn = authState.isAuthenticated;
      final isAuthRoute = state.matchedLocation.startsWith('/auth');
      final isSetupRoute = state.matchedLocation == '/setup';
      final isSetupRequired = authState.isSetupRequired;

      // If setup is required, force to /setup
      if (isSetupRequired && !isSetupRoute) return '/setup';

      // If logged in and on auth route, go to discover
      if (isLoggedIn && isAuthRoute) return '/discover';

      // If not logged in and not on auth/setup route, go to login
      if (!isLoggedIn && !isAuthRoute && !isSetupRoute) return '/auth/login';

      return null;
    },

    routes: [
      // --- Standalone routes (no shell) ---
      GoRoute(
        path: '/auth/login',
        name: RouteNames.login,
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/auth/register',
        name: RouteNames.register,
        builder: (context, state) => const RegisterScreen(),
      ),
      GoRoute(
        path: '/setup',
        name: RouteNames.setup,
        builder: (context, state) => const SetupScreen(),
      ),

      // --- Shell routes (with AdaptiveScaffold) ---
      ShellRoute(
        builder: (context, state, child) => AdaptiveScaffold(child: child),
        routes: [
          GoRoute(
            path: '/discover',
            name: RouteNames.discover,
            builder: (context, state) => const DiscoverScreen(),
          ),
          GoRoute(
            path: '/search',
            name: RouteNames.searchResults,
            builder: (context, state) => const SearchResultsScreen(),
          ),
          GoRoute(
            path: '/media/:id',
            name: RouteNames.mediaDetail,
            builder: (context, state) => MediaDetailScreen(
              mediaId: state.pathParameters['id']!,
            ),
          ),
          GoRoute(
            path: '/list',
            name: RouteNames.myList,
            builder: (context, state) => const MyListScreen(),
          ),
          GoRoute(
            path: '/calendar',
            name: RouteNames.airingCalendar,
            builder: (context, state) => const AiringCalendarScreen(),
          ),
          GoRoute(
            path: '/import',
            name: RouteNames.importList,
            builder: (context, state) => const ImportListScreen(),
          ),
          GoRoute(
            path: '/feed',
            name: RouteNames.feed,
            builder: (context, state) => const FeedScreen(),
          ),
          GoRoute(
            path: '/recommendations',
            name: RouteNames.recommendations,
            builder: (context, state) => const RecommendationsScreen(),
          ),
          GoRoute(
            path: '/discussions',
            name: RouteNames.discussions,
            builder: (context, state) => const DiscussionListScreen(),
          ),
          GoRoute(
            path: '/discussions/:id',
            name: RouteNames.discussionDetail,
            builder: (context, state) => DiscussionDetailScreen(
              discussionId: state.pathParameters['id']!,
            ),
          ),
          GoRoute(
            path: '/watchparty',
            name: RouteNames.watchParty,
            builder: (context, state) => const WatchPartyScreen(),
          ),
          GoRoute(
            path: '/notifications',
            name: RouteNames.notifications,
            builder: (context, state) => const NotificationsScreen(),
          ),
          GoRoute(
            path: '/notifications/preferences',
            name: RouteNames.notificationPreferences,
            builder: (context, state) => const NotificationPreferencesScreen(),
          ),
          GoRoute(
            path: '/profile',
            name: RouteNames.profile,
            builder: (context, state) => const ProfileScreen(),
          ),
          GoRoute(
            path: '/profile/edit',
            name: RouteNames.editProfile,
            builder: (context, state) => const EditProfileScreen(),
          ),
          GoRoute(
            path: '/profile/security',
            name: RouteNames.accountSecurity,
            builder: (context, state) => const AccountSecurityScreen(),
          ),
        ],
      ),
    ],
  );
});
