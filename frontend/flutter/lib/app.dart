import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:otakuhub/core/router/app_router.dart';
import 'package:otakuhub/core/theme/app_theme.dart';
import 'package:otakuhub/core/widgets/search_overlay.dart';

class OtakuHubApp extends ConsumerWidget {
  const OtakuHubApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        // Escape: close any overlay or pop top route
        const SingleActivator(LogicalKeyboardKey.escape): () {
          final navigator = Navigator.of(context, rootNavigator: true);
          if (navigator.canPop()) {
            navigator.pop();
          }
        },
        // Ctrl+K / Meta+K: open search
        const SingleActivator(LogicalKeyboardKey.keyK,
            control: true): () {
          SearchOverlay.show(context);
        },
        const SingleActivator(LogicalKeyboardKey.keyK,
            meta: true): () {
          SearchOverlay.show(context);
        },
        // Ctrl+1..5: navigate to destinations (Home, List, Feed, Alerts, Profile)
        const SingleActivator(LogicalKeyboardKey.digit1,
            control: true): () => _go(context, '/'),
        const SingleActivator(LogicalKeyboardKey.digit2,
            control: true): () => _go(context, '/list'),
        const SingleActivator(LogicalKeyboardKey.digit3,
            control: true): () => _go(context, '/feed'),
        const SingleActivator(LogicalKeyboardKey.digit4,
            control: true): () => _go(context, '/notifications'),
        const SingleActivator(LogicalKeyboardKey.digit5,
            control: true): () => _go(context, '/profile'),
      },
      child: Focus(
        autofocus: true,
        child: MaterialApp.router(
          title: 'OtakuHub',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.dark,
          routerConfig: router,
        ),
      ),
    );
  }

  void _go(BuildContext context, String path) {
    // Navigate without popping the auth guard
    if (GoRouter.of(context).canPop()) {
      GoRouter.of(context).go(path);
    }
  }
}
