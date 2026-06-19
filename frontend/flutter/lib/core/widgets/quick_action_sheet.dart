import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — QuickActionSheet: bottom sheet for quick status/actions on a media.
///
/// Shows status options (watching/reading/completed/etc), score, notes shortcut.
/// Dismissed via drag or tap on scrim.
class QuickActionSheet extends StatelessWidget {
  final String mediaTitle;
  final String? currentStatus;
  final double? currentScore;
  final int? currentProgress;
  final int? maxProgress;
  final ValueChanged<String>? onStatusChanged;
  final ValueChanged<double>? onScoreChanged;
  final VoidCallback? onNotes;
  final VoidCallback? onRemove;

  const QuickActionSheet({
    super.key,
    required this.mediaTitle,
    this.currentStatus,
    this.currentScore,
    this.currentProgress,
    this.maxProgress,
    this.onStatusChanged,
    this.onScoreChanged,
    this.onNotes,
    this.onRemove,
  });

  static const _statuses = [
    'watching',
    'completed',
    'plan_to_watch',
    'paused',
    'dropped',
  ];

  static const _mangaStatuses = [
    'reading',
    'completed',
    'plan_to_read',
    'paused',
    'dropped',
  ];

  /// Show the bottom sheet.
  static Future<void> show({
    required BuildContext context,
    required String mediaTitle,
    String? currentStatus,
    double? currentScore,
    int? currentProgress,
    int? maxProgress,
    ValueChanged<String>? onStatusChanged,
    ValueChanged<double>? onScoreChanged,
    VoidCallback? onNotes,
    VoidCallback? onRemove,
  }) {
    return showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (_) => QuickActionSheet(
        mediaTitle: mediaTitle,
        currentStatus: currentStatus,
        currentScore: currentScore,
        currentProgress: currentProgress,
        maxProgress: maxProgress,
        onStatusChanged: onStatusChanged,
        onScoreChanged: onScoreChanged,
        onNotes: onNotes,
        onRemove: onRemove,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final bottomPadding = MediaQuery.of(context).padding.bottom;
    final statuses = mediaTitle.contains('reading') ||
            mediaTitle.contains('manga') ||
            mediaTitle.contains('manhwa')
        ? _mangaStatuses
        : _statuses;

    return Container(
      padding: EdgeInsets.only(bottom: bottomPadding),
      decoration: BoxDecoration(
        color: tokens.bgSurface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              margin: const EdgeInsets.only(top: 10, bottom: 8),
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                color: tokens.textTertiary,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          // Title
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              mediaTitle,
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: tokens.textPrimary,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          const SizedBox(height: 16),
          // Status options
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Wrap(
              spacing: 8,
              runSpacing: 8,
              children: statuses.map((status) {
                final isSelected = status == currentStatus;
                final statusColor = tokens.statusColor(status);

                return GestureDetector(
                  onTap: () {
                    onStatusChanged?.call(status);
                    Navigator.of(context).pop();
                  },
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 10,
                    ),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? statusColor.withValues(alpha: 0.16)
                          : tokens.bgSurfaceAlt,
                      borderRadius: BorderRadius.circular(tokens.radiusPill),
                      border: Border.all(
                        color: isSelected
                            ? statusColor.withValues(alpha: 0.3)
                            : tokens.borderSubtle,
                      ),
                    ),
                    child: Text(
                      status.replaceAll('_', ' ').split(' ').map(
                            (w) => w.isNotEmpty
                                ? '${w[0].toUpperCase()}${w.substring(1)}'
                                : '',
                          ).join(' '),
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: isSelected ? statusColor : tokens.textPrimary,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 20),
          // Score row
          if (onScoreChanged != null) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Row(
                children: [
                  Icon(Icons.star_rounded,
                      size: 18, color: tokens.accentAmber),
                  const SizedBox(width: 8),
                  Text(
                    currentScore != null
                        ? 'Score: ${currentScore!.toStringAsFixed(1)}'
                        : 'Set score',
                    style: TextStyle(
                      fontFamily: 'Plus Jakarta Sans',
                      fontSize: 14,
                      color: tokens.textPrimary,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
          // Notes shortcut
          if (onNotes != null) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: InkWell(
                onTap: () {
                  Navigator.of(context).pop();
                  onNotes?.call();
                },
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(
                    children: [
                      Icon(Icons.note_alt_rounded,
                          size: 18, color: tokens.textSecondary),
                      const SizedBox(width: 8),
                      Text(
                        'Notes',
                        style: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          fontSize: 14,
                          color: tokens.textPrimary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],
          // Remove
          if (onRemove != null) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: InkWell(
                onTap: () {
                  Navigator.of(context).pop();
                  onRemove?.call();
                },
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Row(
                    children: [
                      Icon(Icons.delete_outline_rounded,
                          size: 18, color: tokens.accentRose),
                      const SizedBox(width: 8),
                      Text(
                        'Remove from list',
                        style: TextStyle(
                          fontFamily: 'Plus Jakarta Sans',
                          fontSize: 14,
                          color: tokens.accentRose,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 8),
          ],
          // Bottom safe area
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}
