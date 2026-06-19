import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — ScoreChip: a small pill showing the score with color coding.
///
/// Renders ★ 8.7 with bg = score color @ 16% alpha.
/// Unrated shows a hollow star + – in text.tertiary.
class ScoreChip extends StatelessWidget {
  final double? score;
  final double size;
  final bool compact;

  const ScoreChip({
    super.key,
    this.score,
    this.size = 48,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final color = tokens.scoreColor(score);

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 4 : 6,
        vertical: compact ? 1 : 2,
      ),
      decoration: BoxDecoration(
        color: score != null ? color.withValues(alpha: 0.16) : Colors.transparent,
        borderRadius: BorderRadius.circular(tokens.radiusPill),
        border: score == null ? Border.all(color: tokens.borderSubtle) : null,
      ),
      child: Text(
        score != null ? '★ ${score!.toStringAsFixed(1)}' : '★ –',
        style: TextStyle(
          fontFamily: 'Plus Jakarta Sans',
          fontSize: compact ? 10 : 11,
          fontWeight: FontWeight.w600,
          height: 1.3,
          color: color,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}
