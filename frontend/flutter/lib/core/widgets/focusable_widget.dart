import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:otakuhub/core/theme/app_colors.dart';

/// Wraps a child widget with Focus + focus border for TV D-pad navigation.
///
/// When the widget receives focus (via D-pad arrow keys), a 2px accent-primary
/// border is rendered around it. The optional [onPress] callback is triggered
/// when the user presses "Select" (Enter / D-pad center) while focused.
///
/// Usage:
/// ```dart
/// FocusableWidget(
///   onPress: () => _navigateToDetail(),
///   child: MediaCard(...),
/// )
/// ```
class FocusableWidget extends StatefulWidget {
  final Widget child;
  final VoidCallback? onPress;
  final String? semanticLabel;
  final bool autofocus;
  final EdgeInsetsGeometry? margin;
  final double scale;

  const FocusableWidget({
    super.key,
    required this.child,
    this.onPress,
    this.semanticLabel,
    this.autofocus = false,
    this.margin,
    this.scale = 1.0,
  });

  @override
  State<FocusableWidget> createState() => _FocusableWidgetState();
}

class _FocusableWidgetState extends State<FocusableWidget> {
  late FocusNode _focusNode;
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode(
      canRequestFocus: true,
    );
    _focusNode.addListener(_onFocusChange);
  }

  @override
  void dispose() {
    _focusNode.removeListener(_onFocusChange);
    _focusNode.dispose();
    super.dispose();
  }

  void _onFocusChange() {
    if (_isFocused != _focusNode.hasFocus) {
      setState(() => _isFocused = _focusNode.hasFocus);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: widget.semanticLabel,
      child: Focus(
        focusNode: _focusNode,
        autofocus: widget.autofocus,
        onKeyEvent: (node, event) {
          if (event is KeyDownEvent &&
              (event.logicalKey == LogicalKeyboardKey.select ||
                  event.logicalKey == LogicalKeyboardKey.enter ||
                  event.logicalKey == LogicalKeyboardKey.space)) {
            widget.onPress?.call();
            return KeyEventResult.handled;
          }
          return KeyEventResult.ignored;
        },
        child: GestureDetector(
          onTap: widget.onPress,
          child: Container(
            margin: widget.margin ?? EdgeInsets.zero,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              border: _isFocused
                  ? Border.all(color: AppColors.accentPrimary, width: 2)
                  : null,
            ),
            child: AnimatedScale(
              scale: _isFocused ? widget.scale * 1.05 : widget.scale,
              duration: const Duration(milliseconds: 150),
              child: widget.child,
            ),
          ),
        ),
      ),
    );
  }
}

/// A focusable wrapper specifically for list tiles and cards,
/// providing a subtle focus highlight via a colored background overlay.
class FocusableTile extends StatefulWidget {
  final Widget child;
  final VoidCallback? onTap;
  final String? semanticLabel;

  const FocusableTile({
    super.key,
    required this.child,
    this.onTap,
    this.semanticLabel,
  });

  @override
  State<FocusableTile> createState() => _FocusableTileState();
}

class _FocusableTileState extends State<FocusableTile> {
  late FocusNode _focusNode;
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode(canRequestFocus: true);
    _focusNode.addListener(_onFocusChange);
  }

  @override
  void dispose() {
    _focusNode.removeListener(_onFocusChange);
    _focusNode.dispose();
    super.dispose();
  }

  void _onFocusChange() {
    if (_isFocused != _focusNode.hasFocus) {
      setState(() => _isFocused = _focusNode.hasFocus);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: widget.semanticLabel,
      child: Focus(
        focusNode: _focusNode,
        onKeyEvent: (node, event) {
          if (event is KeyDownEvent &&
              (event.logicalKey == LogicalKeyboardKey.select ||
                  event.logicalKey == LogicalKeyboardKey.enter ||
                  event.logicalKey == LogicalKeyboardKey.space)) {
            widget.onTap?.call();
            return KeyEventResult.handled;
          }
          return KeyEventResult.ignored;
        },
        child: GestureDetector(
          onTap: widget.onTap,
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: _isFocused
                  ? AppColors.accentPrimary.withAlpha(25)
                  : Colors.transparent,
              border: _isFocused
                  ? Border.all(color: AppColors.accentPrimary, width: 2)
                  : null,
            ),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              child: widget.child,
            ),
          ),
        ),
      ),
    );
  }
}
