import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/platform/tv_detector.dart';
import 'package:otakuhub/features/notifications/providers/notification_providers.dart';
import 'package:go_router/go_router.dart';

class AdaptiveScaffold extends StatelessWidget {
  final Widget child;

  const AdaptiveScaffold({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final width = constraints.maxWidth;

        if (TVDetector.isTV(context)) {
          return _TvScaffold(child: child);
        }
        if (width < 600) {
          return _MobileScaffold(child: child);
        } else if (width < 1024) {
          return _TabletScaffold(child: child);
        } else {
          return _DesktopScaffold(child: child);
        }
      },
    );
  }
}

// --- Notification badge widget ---
class _NotificationBadgeIcon extends ConsumerWidget {
  final IconData icon;

  const _NotificationBadgeIcon({required this.icon});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final unreadCount = ref.watch(unreadNotificationCountProviderProvider);
    final count = unreadCount.asData?.value ?? 0;
    if (count > 0) {
      return Badge(
        label: Text(count > 99 ? '99+' : count.toString()),
        child: Icon(icon),
      );
    }
    return Icon(icon);
  }
}

// --- Mobile (<600px) ---
class _MobileScaffold extends StatelessWidget {
  final Widget child;

  const _MobileScaffold({required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex(context),
        onDestinationSelected: (index) => _navigate(context, index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.explore_outlined), label: 'Discover'),
          NavigationDestination(icon: Icon(Icons.list_alt_outlined), label: 'My List'),
          NavigationDestination(icon: Icon(Icons.feed_outlined), label: 'Feed'),
          NavigationDestination(icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined), label: 'Alerts'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
      ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/calendar')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions') || location.startsWith('/watchparty')) return 2;
    if (location.startsWith('/notifications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.discover);
      case 1: context.goNamed(RouteNames.myList);
      case 2: context.goNamed(RouteNames.feed);
      case 3: context.goNamed(RouteNames.notifications);
      case 4: context.goNamed(RouteNames.profile);
    }
  }
}

// --- Tablet (600-1024px) ---
class _TabletScaffold extends StatelessWidget {
  final Widget child;

  const _TabletScaffold({required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _currentIndex(context),
            onDestinationSelected: (index) => _navigate(context, index),
            labelType: NavigationRailLabelType.all,
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.explore_outlined),
                label: Text('Discover'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.list_alt_outlined),
                label: Text('My List'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.feed_outlined),
                label: Text('Feed'),
              ),
              NavigationRailDestination(
                icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined),
                selectedIcon: _NotificationBadgeIcon(icon: Icons.notifications),
                label: Text('Alerts'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.person_outline),
                label: Text('Profile'),
              ),
            ],
          ),
          const VerticalDivider(width: 1),
          Expanded(child: child),
        ],
      ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/calendar')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions') || location.startsWith('/watchparty')) return 2;
    if (location.startsWith('/notifications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.discover);
      case 1: context.goNamed(RouteNames.myList);
      case 2: context.goNamed(RouteNames.feed);
      case 3: context.goNamed(RouteNames.notifications);
      case 4: context.goNamed(RouteNames.profile);
    }
  }
}

// --- Desktop (>1024px) ---
class _DesktopScaffold extends StatelessWidget {
  final Widget child;

  const _DesktopScaffold({required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _currentIndex(context),
            onDestinationSelected: (index) => _navigate(context, index),
            labelType: NavigationRailLabelType.none,
            extended: true,
            minExtendedWidth: 200,
            leading: Padding(
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
              child: Row(
                children: [
                  Icon(Icons.movie_creation_rounded,
                      color: AppColors.accentPrimary, size: 28),
                  const SizedBox(width: 8),
                  Text(
                    'OtakuHub',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AppColors.textPrimary,
                        ),
                  ),
                ],
              ),
            ),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.explore_outlined),
                selectedIcon: Icon(Icons.explore),
                label: Text('Discover'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.list_alt_outlined),
                selectedIcon: Icon(Icons.list_alt),
                label: Text('My List'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.feed_outlined),
                selectedIcon: Icon(Icons.feed),
                label: Text('Feed'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.party_mode_outlined),
                selectedIcon: Icon(Icons.party_mode),
                label: Text('Watch Party'),
              ),
              NavigationRailDestination(
                icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined),
                selectedIcon: _NotificationBadgeIcon(icon: Icons.notifications),
                label: Text('Alerts'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.person_outline),
                selectedIcon: Icon(Icons.person),
                label: Text('Profile'),
              ),
            ],
          ),
          const VerticalDivider(width: 1),
          Expanded(child: child),
        ],
      ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/calendar')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions')) return 2;
    if (location.startsWith('/watchparty')) return 3;
    if (location.startsWith('/notifications')) return 4;
    if (location.startsWith('/profile')) return 5;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.discover);
      case 1: context.goNamed(RouteNames.myList);
      case 2: context.goNamed(RouteNames.feed);
      case 3: context.goNamed(RouteNames.watchParty);
      case 4: context.goNamed(RouteNames.notifications);
      case 5: context.goNamed(RouteNames.profile);
    }
  }
}

// --- TV (large landscape, D-pad focused) ---
class _TvScaffold extends StatelessWidget {
  final Widget child;

  const _TvScaffold({required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: _currentIndex(context),
            onDestinationSelected: (index) => _navigate(context, index),
            labelType: NavigationRailLabelType.all,
            minExtendedWidth: 180,
            leading: Padding(
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
              child: Icon(
                Icons.movie_creation_rounded,
                color: AppColors.accentPrimary,
                size: 32,
              ),
            ),
            destinations: const [
              NavigationRailDestination(
                icon: Icon(Icons.explore_outlined, size: 28),
                label: Text('Discover'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.list_alt_outlined, size: 28),
                label: Text('My List'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.feed_outlined, size: 28),
                label: Text('Feed'),
              ),
              NavigationRailDestination(
                icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined),
                label: Text('Alerts'),
              ),
              NavigationRailDestination(
                icon: Icon(Icons.person_outline, size: 28),
                label: Text('Profile'),
              ),
            ],
          ),
          Expanded(
            child: FocusScope(
              child: child,
            ),
          ),
        ],
      ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/calendar')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions') || location.startsWith('/watchparty')) return 2;
    if (location.startsWith('/notifications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.discover);
      case 1: context.goNamed(RouteNames.myList);
      case 2: context.goNamed(RouteNames.feed);
      case 3: context.goNamed(RouteNames.notifications);
      case 4: context.goNamed(RouteNames.profile);
    }
  }
}
