import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — AppToast: minimal overlay toast for quick feedback.
///
/// Types:
/// - success: accentMint bg
/// - error: destructive bg
/// - info: accentPrimary bg
/// - warning: warning bg (accentYellow)
///
/// Shown via [AppToast.show] which inserts into the overlay.
class AppToast {
  AppToast._();

  /// Show a toast at the top of the screen.
  static void show({
    required BuildContext context,
    required String message,
    AppToastType type = AppToastType.info,
    Duration duration = const Duration(seconds: 3),
  }) {
    final tokens = context.tokens;

    Color bgColor;
    IconData icon;

    switch (type) {
      case AppToastType.success:
        bgColor = tokens.accentMint;
        icon = Icons.check_circle_rounded;
      case AppToastType.error:
        bgColor = tokens.accentRose;
        icon = Icons.error_rounded;
      case AppToastType.info:
        bgColor = tokens.accentPrimary;
        icon = Icons.info_rounded;
      case AppToastType.warning:
        bgColor = tokens.accentAmber;
        icon = Icons.warning_rounded;
    }

    final overlay = Overlay.of(context);
    late OverlayEntry entry;

    entry = OverlayEntry(
      builder: (context) => _ToastWidget(
        message: message,
        bgColor: bgColor,
        icon: icon,
        onDismiss: () => entry.remove(),
        duration: duration,
      ),
    );

    overlay.insert(entry);

    // Auto-dismiss
    Future.delayed(duration, () {
      if (entry.mounted) entry.remove();
    });
  }
}

enum AppToastType { success, error, info, warning }

class _ToastWidget extends StatefulWidget {
  final String message;
  final Color bgColor;
  final IconData icon;
  final VoidCallback onDismiss;
  final Duration duration;

  const _ToastWidget({
    required this.message,
    required this.bgColor,
    required this.icon,
    required this.onDismiss,
    required this.duration,
  });

  @override
  State<_ToastWidget> createState() => _ToastWidgetState();
}

class _ToastWidgetState extends State<_ToastWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slideAnim;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );

    _slideAnim = Tween<Offset>(
      begin: const Offset(0, -1.5),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
      reverseCurve: Curves.easeInCubic,
    ));

    _fadeAnim = Tween<double>(begin: 0, end: 1).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
      reverseCurve: Curves.easeInCubic,
    ));

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void dismiss() {
    _controller.reverse().then((_) => widget.onDismiss());
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Positioned(
      top: MediaQuery.of(context).padding.top + 8,
      left: tokens.spaceMd,
      right: tokens.spaceMd,
      child: SlideTransition(
        position: _slideAnim,
        child: FadeTransition(
          opacity: _fadeAnim,
          child: GestureDetector(
            onTap: dismiss,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: widget.bgColor,
                borderRadius: BorderRadius.circular(tokens.radiusSm),
                boxShadow: [
                  BoxShadow(
                    color: widget.bgColor.withValues(alpha: 0.3),
                    blurRadius: 16,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Icon(widget.icon, size: 20, color: Colors.white),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      widget.message,
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 14,
                        fontWeight: FontWeight.w500,
                        color: Colors.white,
                        height: 1.3,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
