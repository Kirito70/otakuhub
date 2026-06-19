import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — ProgressControl: inline episode/chapter stepper.
///
/// Layout: –  Ep 5 / 12  +
/// +/- are 32px circular targets. Center tappable → number pad.
/// Thin progress bar when maxProgress is known.
class ProgressControl extends StatefulWidget {
  final int progress;
  final int maxProgress;
  final String label;
  final ValueChanged<int> onProgressChanged;

  const ProgressControl({
    super.key,
    required this.progress,
    required this.maxProgress,
    this.label = 'Ep',
    required this.onProgressChanged,
  });

  @override
  State<ProgressControl> createState() => _ProgressControlState();
}

class _ProgressControlState extends State<ProgressControl> {
  late int _progress;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _progress = widget.progress;
  }

  @override
  void didUpdateWidget(ProgressControl oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.progress != widget.progress) {
      _progress = widget.progress;
    }
  }

  Future<void> _change(int delta) async {
    final newProgress = (_progress + delta).clamp(0, widget.maxProgress);
    if (newProgress == _progress) return;

    setState(() {
      _progress = newProgress;
      _isLoading = true;
    });

    try {
      widget.onProgressChanged(_progress);
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showNumberPad() {
    // TODO: show modal number-pad sheet for direct entry
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Decrement
            _CircleButton(
              icon: Icons.remove_rounded,
              onTap: () => _change(-1),
              enabled: _progress > 0,
              tokens: tokens,
            ),
            const SizedBox(width: 8),
            // Center label (tappable)
            GestureDetector(
              onTap: _showNumberPad,
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 240),
                transitionBuilder: (child, anim) => SlideTransition(
                  position: Tween<Offset>(
                    begin: const Offset(0, -0.3),
                    end: Offset.zero,
                  ).animate(CurvedAnimation(
                    parent: anim,
                    curve: Curves.easeOutCubic,
                  )),
                  child: FadeTransition(opacity: anim, child: child),
                ),
                child: Text(
                  _isLoading
                      ? '—'
                      : '${widget.label} $_progress / ${widget.maxProgress}',
                  key: ValueKey('$_progress-${widget.maxProgress}'),
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: tokens.textPrimary,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 8),
            // Increment
            _CircleButton(
              icon: Icons.add_rounded,
              onTap: () => _change(1),
              enabled: _progress < widget.maxProgress,
              tokens: tokens,
            ),
          ],
        ),
        // Progress bar
        if (widget.maxProgress > 0)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(2),
              child: LinearProgressIndicator(
                value: _progress / widget.maxProgress,
                backgroundColor: tokens.bgSurfaceAlt,
                valueColor: AlwaysStoppedAnimation(tokens.accentMint),
                minHeight: 3,
              ),
            ),
          ),
      ],
    );
  }
}

class _CircleButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final bool enabled;
  final AppTokens tokens;

  const _CircleButton({
    required this.icon,
    required this.onTap,
    required this.enabled,
    required this.tokens,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: enabled ? onTap : null,
      child: AnimatedOpacity(
        duration: const Duration(milliseconds: 160),
        opacity: enabled ? 1.0 : 0.38,
        child: Container(
          width: 32,
          height: 32,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: tokens.bgSurfaceAlt,
            border: Border.all(color: tokens.borderSubtle),
          ),
          child: Icon(icon, size: 16, color: tokens.textPrimary),
        ),
      ),
    );
  }
}
