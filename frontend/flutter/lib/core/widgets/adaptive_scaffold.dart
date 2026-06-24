import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/platform/tv_detector.dart';
import 'package:otakuhub/features/notifications/providers/notification_providers.dart';
import 'package:otakuhub/core/widgets/search_overlay.dart';
import 'package:go_router/go_router.dart';

/// ADR 094 — AdaptiveScaffold / NavigationScaffold: responsive shell.
///
/// Breakpoints:
/// - compact (<600): bottom NavigationBar (mobile) + AppBar with search icon
/// - medium (600-1024): NavigationRail + top header bar with search input
/// - expanded (>1024): extended NavigationRail + top header bar with search input
/// - TV: D-pad focused NavigationRail with 1.15× scale
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

  const _NotificationBadgeIcon({
    required this.icon,
  });

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

// ---------------------------------------------------------------------------
// Shared search bar widget (for desktop/tablet header)
// ---------------------------------------------------------------------------
class _SearchHeaderBar extends ConsumerStatefulWidget {
  const _SearchHeaderBar();

  @override
  ConsumerState<_SearchHeaderBar> createState() => _SearchHeaderBarState();
}

class _SearchHeaderBarState extends ConsumerState<_SearchHeaderBar> {
  final _controller = TextEditingController();
  final _focusNode = FocusNode();

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onSubmit() {
    final query = _controller.text.trim();
    if (query.isNotEmpty) {
      SearchOverlay.show(context, initialQuery: query);
    }
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: tokens.bgSurface,
        border: Border(
          bottom: BorderSide(color: tokens.borderSubtle, width: 1),
        ),
      ),
      child: Semantics(
        label: 'Search anime, manga, and manhwa',
        child: TextField(
          controller: _controller,
          focusNode: _focusNode,
          onSubmitted: (_) => _onSubmit(),
          style: TextStyle(
            fontFamily: 'Plus Jakarta Sans',
            fontSize: 14,
            color: tokens.textPrimary,
          ),
          decoration: InputDecoration(
            hintText: 'Search anime, manga, manhwa…',
            hintStyle: TextStyle(
              fontFamily: 'Plus Jakarta Sans',
              fontSize: 14,
              color: tokens.textTertiary,
            ),
            prefixIcon: Icon(
              Icons.search_rounded,
              size: 20,
              color: tokens.textTertiary,
            ),
            suffixIcon: _controller.text.isNotEmpty
                ? Semantics(
                    label: 'Clear search',
                    child: IconButton(
                      icon: Icon(Icons.close_rounded,
                          size: 18, color: tokens.textTertiary),
                      onPressed: () {
                        _controller.clear();
                        _focusNode.requestFocus();
                      },
                      tooltip: 'Clear',
                    ),
                  )
                : Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: tokens.bgSurfaceAlt,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.keyboard_command_key_rounded,
                              size: 12, color: tokens.textTertiary),
                          const SizedBox(width: 3),
                          Text(
                            'K',
                            style: TextStyle(
                              fontFamily: 'Plus Jakarta Sans',
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: tokens.textTertiary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
            filled: true,
            fillColor: tokens.bgSurfaceAlt,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: tokens.borderSubtle),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: tokens.borderSubtle),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide:
                  BorderSide(color: tokens.accentPrimary, width: 1.5),
            ),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            isDense: true,
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Keyboard shortcut bindings for search (Ctrl+K / Cmd+K)
// ---------------------------------------------------------------------------
Map<ShortcutActivator, VoidCallback> _searchShortcuts(BuildContext context) => {
  SingleActivator(LogicalKeyboardKey.keyK, control: true): () => SearchOverlay.show(context),
  SingleActivator(LogicalKeyboardKey.keyK, meta: true): () => SearchOverlay.show(context),
};

// --- Mobile (<600px) ---
class _MobileScaffold extends StatelessWidget {
  final Widget child;

  const _MobileScaffold({required this.child});

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return CallbackShortcuts(
      bindings: _searchShortcuts(context),
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: tokens.bgSurface,
          elevation: 0,
          scrolledUnderElevation: 0,
          title: Semantics(
            label: 'Search',
            child: GestureDetector(
              onTap: () => SearchOverlay.show(context),
              child: Container(
                height: 40,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  color: tokens.bgSurfaceAlt,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: tokens.borderSubtle),
                ),
                child: Row(
                  children: [
                    Icon(Icons.search_rounded,
                        size: 18, color: tokens.textTertiary),
                    const SizedBox(width: 8),
                    Text(
                      'Search anime, manga…',
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 14,
                        color: tokens.textTertiary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        body: child,
        bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex(context),
        onDestinationSelected: (index) => _navigate(context, index),
        backgroundColor: tokens.bgSurface,
        indicatorColor: tokens.accentPrimary.withValues(alpha: 0.12),
        destinations: [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home, color: tokens.accentPrimary),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.list_alt_outlined),
            selectedIcon: Icon(Icons.list_alt, color: tokens.accentPrimary),
            label: 'My List',
          ),
          NavigationDestination(
            icon: Icon(Icons.feed_outlined),
            selectedIcon: Icon(Icons.feed, color: tokens.accentPrimary),
            label: 'Feed',
          ),
          NavigationDestination(
            icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined),
            selectedIcon: _NotificationBadgeIcon(icon: Icons.notifications),
            label: 'Alerts',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person, color: tokens.accentPrimary),
            label: 'Profile',
          ),
        ],
      ),
    ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/import')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions') || location.startsWith('/watchparty')) return 2;
    if (location.startsWith('/notifications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.home);
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
    final tokens = context.tokens;

    return CallbackShortcuts(
      bindings: _searchShortcuts(context),
      child: Scaffold(
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: _currentIndex(context),
              onDestinationSelected: (index) => _navigate(context, index),
              labelType: NavigationRailLabelType.all,
              backgroundColor: tokens.bgSurface,
              indicatorColor: tokens.accentPrimary.withValues(alpha: 0.12),
              leading: Padding(
                padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                child: Icon(
                  Icons.movie_creation_rounded,
                  color: tokens.accentPrimary,
                  size: 28,
                ),
              ),
              destinations: [
                NavigationRailDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home, color: tokens.accentPrimary),
                  label: const Text('Home'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.list_alt_outlined),
                  selectedIcon: Icon(Icons.list_alt, color: tokens.accentPrimary),
                  label: const Text('My List'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.feed_outlined),
                  selectedIcon: Icon(Icons.feed, color: tokens.accentPrimary),
                  label: const Text('Feed'),
                ),
                NavigationRailDestination(
                  icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined),
                  selectedIcon: _NotificationBadgeIcon(icon: Icons.notifications),
                  label: const Text('Alerts'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.person_outline),
                  selectedIcon: Icon(Icons.person, color: tokens.accentPrimary),
                  label: const Text('Profile'),
                ),
              ],
            ),
            const VerticalDivider(width: 1),
            Expanded(
              child: Column(
                children: [
                  const _SearchHeaderBar(),
                  Expanded(child: child),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/import')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions') || location.startsWith('/watchparty')) return 2;
    if (location.startsWith('/notifications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.home);
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
    final tokens = context.tokens;

    return CallbackShortcuts(
      bindings: _searchShortcuts(context),
      child: Scaffold(
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: _currentIndex(context),
              onDestinationSelected: (index) => _navigate(context, index),
              labelType: NavigationRailLabelType.none,
              extended: true,
              minExtendedWidth: 200,
              backgroundColor: tokens.bgSurface,
              indicatorColor: tokens.accentPrimary.withValues(alpha: 0.12),
              leading: Padding(
                padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 16),
                child: Row(
                  children: [
                    Icon(
                      Icons.movie_creation_rounded,
                      color: tokens.accentPrimary,
                      size: 28,
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'OtakuHub',
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        color: tokens.textPrimary,
                      ),
                    ),
                  ],
                ),
              ),
              destinations: [
                NavigationRailDestination(
                  icon: Icon(Icons.home_outlined),
                  selectedIcon: Icon(Icons.home, color: tokens.accentPrimary),
                  label: const Text('Home'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.list_alt_outlined),
                  selectedIcon: Icon(Icons.list_alt, color: tokens.accentPrimary),
                  label: const Text('My List'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.feed_outlined),
                  selectedIcon: Icon(Icons.feed, color: tokens.accentPrimary),
                  label: const Text('Feed'),
                ),
                NavigationRailDestination(
                  icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined),
                  selectedIcon: _NotificationBadgeIcon(icon: Icons.notifications),
                  label: const Text('Alerts'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.person_outline),
                  selectedIcon: Icon(Icons.person, color: tokens.accentPrimary),
                  label: const Text('Profile'),
                ),
              ],
            ),
            const VerticalDivider(width: 1),
            Expanded(
              child: Column(
                children: [
                  const _SearchHeaderBar(),
                  Expanded(child: child),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/import')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions') || location.startsWith('/watchparty')) return 2;
    if (location.startsWith('/notifications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.home);
      case 1: context.goNamed(RouteNames.myList);
      case 2: context.goNamed(RouteNames.feed);
      case 3: context.goNamed(RouteNames.notifications);
      case 4: context.goNamed(RouteNames.profile);
    }
  }
}

// --- TV (large landscape, D-pad focused) ---
class _TvScaffold extends StatelessWidget {
  final Widget child;

  const _TvScaffold({required this.child});

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return CallbackShortcuts(
      bindings: _searchShortcuts(context),
      child: Scaffold(
        body: Row(
          children: [
            NavigationRail(
              selectedIndex: _currentIndex(context),
              onDestinationSelected: (index) => _navigate(context, index),
              labelType: NavigationRailLabelType.all,
              minExtendedWidth: 180,
              backgroundColor: tokens.bgSurface,
              indicatorColor: tokens.accentPrimary.withValues(alpha: 0.12),
              leading: Padding(
                padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                child: Icon(
                  Icons.movie_creation_rounded,
                  color: tokens.accentPrimary,
                  size: 32,
                ),
              ),
              destinations: [
                NavigationRailDestination(
                  icon: Icon(Icons.home_outlined, size: 28),
                  selectedIcon: Icon(Icons.home, size: 28, color: tokens.accentPrimary),
                  label: const Text('Home'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.list_alt_outlined, size: 28),
                  selectedIcon: Icon(Icons.list_alt, size: 28, color: tokens.accentPrimary),
                  label: const Text('My List'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.feed_outlined, size: 28),
                  selectedIcon: Icon(Icons.feed, size: 28, color: tokens.accentPrimary),
                  label: const Text('Feed'),
                ),
                NavigationRailDestination(
                  icon: _NotificationBadgeIcon(icon: Icons.notifications_outlined),
                  selectedIcon: _NotificationBadgeIcon(icon: Icons.notifications),
                  label: const Text('Alerts'),
                ),
                NavigationRailDestination(
                  icon: Icon(Icons.person_outline, size: 28),
                  selectedIcon: Icon(Icons.person, size: 28, color: tokens.accentPrimary),
                  label: const Text('Profile'),
                ),
              ],
            ),
            Expanded(
              child: FocusScope(
                child: Column(
                  children: [
                    Expanded(child: child),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  int _currentIndex(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;
    if (location.startsWith('/list') || location.startsWith('/import')) return 1;
    if (location.startsWith('/feed') || location.startsWith('/recommendations') ||
        location.startsWith('/discussions') || location.startsWith('/watchparty')) return 2;
    if (location.startsWith('/notifications')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }

  void _navigate(BuildContext context, int index) {
    switch (index) {
      case 0: context.goNamed(RouteNames.home);
      case 1: context.goNamed(RouteNames.myList);
      case 2: context.goNamed(RouteNames.feed);
      case 3: context.goNamed(RouteNames.notifications);
      case 4: context.goNamed(RouteNames.profile);
    }
  }
}
