import 'package:flutter/material.dart';

/// ADR 095 — Animation Tokens for OtakuHub.
///
/// All animation durations in the app should reference these tokens,
/// never hardcode `Duration(milliseconds: N)`.
///
/// Access via `Theme.of(context).extension<AnimationTokens>()!`.
/// When reduce motion is active, use [withReducedMotion] to get zero durations.
@immutable
class AnimationTokens extends ThemeExtension<AnimationTokens> {
  /// Press feedback, focus borders (100ms)
  final Duration fast;

  /// Standard transitions (200ms)
  final Duration normal;

  /// Page transitions, hero animations (400ms)
  final Duration slow;

  /// Skeleton shimmer period (1600ms)
  final Duration shimmer;

  /// Toast slide/fade (300ms)
  final Duration toast;

  /// Progress control number crossfade (240ms)
  final Duration progress;

  /// FocusableWidget scale animation (150ms)
  final Duration focusScale;

  /// Score/progress widget opacity transitions (160ms)
  final Duration widgetOpacity;

  /// Staggered card animation delay (400ms stagger total)
  final Duration staggerDelay;

  const AnimationTokens({
    this.fast = const Duration(milliseconds: 100),
    this.normal = const Duration(milliseconds: 200),
    this.slow = const Duration(milliseconds: 400),
    this.shimmer = const Duration(milliseconds: 1600),
    this.toast = const Duration(milliseconds: 300),
    this.progress = const Duration(milliseconds: 240),
    this.focusScale = const Duration(milliseconds: 150),
    this.widgetOpacity = const Duration(milliseconds: 160),
    this.staggerDelay = const Duration(milliseconds: 400),
  });

  /// Dark theme defaults.
  static const AnimationTokens dark = AnimationTokens();

  @override
  AnimationTokens copyWith({
    Duration? fast,
    Duration? normal,
    Duration? slow,
    Duration? shimmer,
    Duration? toast,
    Duration? progress,
    Duration? focusScale,
    Duration? widgetOpacity,
    Duration? staggerDelay,
  }) {
    return AnimationTokens(
      fast: fast ?? this.fast,
      normal: normal ?? this.normal,
      slow: slow ?? this.slow,
      shimmer: shimmer ?? this.shimmer,
      toast: toast ?? this.toast,
      progress: progress ?? this.progress,
      focusScale: focusScale ?? this.focusScale,
      widgetOpacity: widgetOpacity ?? this.widgetOpacity,
      staggerDelay: staggerDelay ?? this.staggerDelay,
    );
  }

  @override
  AnimationTokens lerp(covariant AnimationTokens? other, double t) {
    if (other == null) return this;
    return AnimationTokens(
      fast: lerpDuration(fast, other.fast, t),
      normal: lerpDuration(normal, other.normal, t),
      slow: lerpDuration(slow, other.slow, t),
      shimmer: lerpDuration(shimmer, other.shimmer, t),
      toast: lerpDuration(toast, other.toast, t),
      progress: lerpDuration(progress, other.progress, t),
      focusScale: lerpDuration(focusScale, other.focusScale, t),
      widgetOpacity: lerpDuration(widgetOpacity, other.widgetOpacity, t),
      staggerDelay: lerpDuration(staggerDelay, other.staggerDelay, t),
    );
  }

  /// Linearly interpolate two Durations.
  static Duration lerpDuration(Duration a, Duration b, double t) {
    return Duration(
      milliseconds:
          (a.inMilliseconds + (b.inMilliseconds - a.inMilliseconds) * t)
              .round(),
    );
  }
}

/// Returns [duration] when animations are enabled,
/// or [Duration.zero] when the OS "Reduce motion" accessibility setting is on.
///
/// Usage:
/// ```dart
/// final d = context.maybeAnimDuration(tokens.fast); // respects reduce motion
/// ```
extension ReduceMotionExtension on BuildContext {
  /// Returns the given duration, or Duration.zero if reduce motion is enabled.
  Duration maybeAnimDuration(Duration duration) {
    if (MediaQuery.disableAnimationsOf(this)) return Duration.zero;
    return duration;
  }
}
