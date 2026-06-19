import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — StatusPill: a colored pill showing a watch/read status.
///
/// Color maps via [AppTokens.statusColor]. Optional leading dot.
class StatusPill extends StatelessWidget {
  final String status;
  final bool showDot;
  final double fontSize;

  const StatusPill({
    super.key,
    required this.status,
    this.showDot = false,
    this.fontSize = 11,
  });

  String _label(String status) {
    switch (status) {
      case 'watching':
        return 'Watching';
      case 'reading':
        return 'Reading';
      case 'rewatching':
        return 'Rewatching';
      case 'rereading':
        return 'Rereading';
      case 'completed':
        return 'Completed';
      case 'plan_to_watch':
        return 'Plan';
      case 'plan_to_read':
        return 'Plan';
      case 'paused':
        return 'Paused';
      case 'on_hold':
        return 'On Hold';
      case 'dropped':
        return 'Dropped';
      default:
        return status;
    }
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final color = tokens.statusColor(status);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(tokens.radiusPill),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showDot) ...[
            Container(
              width: 6,
              height: 6,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 4),
          ],
          Text(
            _label(status),
            style: TextStyle(
              fontFamily: 'Plus Jakarta Sans',
              fontSize: fontSize,
              fontWeight: FontWeight.w600,
              color: color,
              height: 1.2,
            ),
          ),
        ],
      ),
    );
  }
}
