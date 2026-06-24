import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/watchparty/models/watch_party.dart';
import 'package:otakuhub/features/watchparty/widgets/date_utils.dart';

class PartyCard extends StatelessWidget {
  final WatchParty party;
  final bool showAttendButton;
  final VoidCallback? onTap;
  final VoidCallback? onAttend;

  const PartyCard({
    super.key,
    required this.party,
    this.showAttendButton = false,
    this.onTap,
    this.onAttend,
  });

  Color _statusColor(String status) {
    switch (status) {
      case 'live':
        return AppColors.success;
      case 'scheduled':
        return AppColors.accentSecondary;
      case 'completed':
        return AppColors.textMuted;
      case 'cancelled':
        return AppColors.destructive;
      default:
        return AppColors.textMuted;
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'live':
        return 'LIVE';
      case 'scheduled':
        return 'SCHEDULED';
      case 'completed':
        return 'COMPLETED';
      case 'cancelled':
        return 'CANCELLED';
      default:
        return status.toUpperCase();
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = date.difference(now);
    if (diff.isNegative) {
      if (diff.abs().inHours < 24) {
        return '${diff.abs().inHours}h ago';
      }
      return formatDateShort(date);
    }
    if (diff.inDays == 0) {
      if (diff.inHours == 0) {
        return 'in ${diff.inMinutes}m';
      }
      return 'in ${diff.inHours}h';
    }
    if (diff.inDays < 7) {
      return 'in ${diff.inDays}d';
    }
    return formatDateShort(date);
  }

  @override
  Widget build(BuildContext context) {
    final color = _statusColor(party.status);
    final semanticLabel = '${party.title ?? "Watch Party"}, status: ${party.status}';

    return MergeSemantics(
      child: Semantics(
        label: semanticLabel,
        child: Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              // Status indicator
              Container(
                width: 4,
                height: 48,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(width: 12),

              // Content
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Title + status badge row
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            party.title ?? 'Watch Party',
                            style: Theme.of(context)
                                .textTheme
                                .bodyLarge
                                ?.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.textPrimary,
                                ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 6,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: color.withValues(alpha: 0.15),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(
                              color: color.withValues(alpha: 0.3),
                            ),
                          ),
                          child: Text(
                            _statusLabel(party.status),
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: color,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),

                    // Episode + date row
                    Row(
                      children: [
                        if (party.episodeNumber != null) ...[
                          Icon(Icons.play_circle_outline,
                              size: 14, color: AppColors.textSecondary),
                          const SizedBox(width: 4),
                          Text(
                            'Ep ${party.episodeNumber}',
                            style: TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                            ),
                          ),
                          const SizedBox(width: 12),
                        ],
                        Icon(Icons.schedule_outlined,
                            size: 14, color: AppColors.textSecondary),
                        const SizedBox(width: 4),
                        Text(
                          _formatDate(party.scheduledAt),
                          style: TextStyle(
                            fontSize: 12,
                            color: AppColors.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // Attend button (upcoming only)
              if (showAttendButton && party.status == 'scheduled')
                Padding(
                  padding: const EdgeInsets.only(left: 8),
                  child: SizedBox(
                    height: 32,
                    child: ElevatedButton(
                      onPressed: onAttend,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.accentPrimary,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                        textStyle: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      child: const Text('Attend'),
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
