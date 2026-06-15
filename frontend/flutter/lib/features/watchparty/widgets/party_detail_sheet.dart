import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/watchparty/models/watch_party.dart';
import 'package:otakuhub/features/watchparty/providers/watch_party_provider.dart';
import 'package:otakuhub/features/watchparty/widgets/date_utils.dart';

class PartyDetailSheet extends ConsumerWidget {
  final String partyId;

  const PartyDetailSheet({super.key, required this.partyId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(partyDetailProviderProvider(partyId));
    final rsvpsAsync = ref.watch(partyRsvpsProviderProvider(partyId));

    return DraggableScrollableSheet(
      initialChildSize: 0.75,
      minChildSize: 0.5,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) {
        return Container(
          decoration: BoxDecoration(
            color: const Color(0xFF111111),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: detailAsync.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (err, _) => Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline,
                        color: AppColors.destructive, size: 48),
                    const SizedBox(height: 12),
                    Text(
                      'Failed to load party details',
                      style: TextStyle(color: AppColors.textSecondary),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: () => ref.invalidate(
                        partyDetailProviderProvider(partyId),
                      ),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
            data: (WatchPartyDetail detail) => _buildDetailContent(
              context, ref, detail, rsvpsAsync, scrollController,
            ),
          ),
        );
      },
    );
  }

  Widget _buildDetailContent(
    BuildContext context,
    WidgetRef ref,
    WatchPartyDetail detail,
    AsyncValue<WatchPartyRsvpListResponse> rsvpsAsync,
    ScrollController scrollController,
  ) {
    return ListView(
      controller: scrollController,
      padding: EdgeInsets.zero,
      children: [
        // Drag handle
        Center(
          child: Container(
            margin: const EdgeInsets.symmetric(vertical: 12),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.white.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
        ),

        // Title
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Text(
            detail.title ?? 'Watch Party',
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
          ),
        ),
        const SizedBox(height: 8),

        // Status badge
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: _StatusBadge(status: detail.status),
        ),
        const SizedBox(height: 20),

        // Info sections
        _InfoRow(
          icon: Icons.person_outline,
          label: 'Hosted by',
          value: detail.hostDisplayName ?? detail.hostUsername ?? 'Unknown',
        ),
        if (detail.mediaTitle != null)
          _InfoRow(
            icon: Icons.movie_outlined,
            label: 'Media',
            value: detail.mediaTitle!,
          ),
        if (detail.episodeNumber != null)
          _InfoRow(
            icon: Icons.play_circle_outline,
            label: 'Episode',
            value: 'Episode ${detail.episodeNumber}',
          ),
        _InfoRow(
          icon: Icons.schedule_outlined,
          label: 'When',
          value: formatDateFull(detail.scheduledAt),
        ),
        if (detail.notes != null && detail.notes!.isNotEmpty) ...[
          const SizedBox(height: 12),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            child: Text(
              detail.notes!,
              style: TextStyle(
                fontSize: 14,
                color: AppColors.textSecondary,
                height: 1.5,
              ),
            ),
          ),
        ],

        const SizedBox(height: 24),

        // RSVP actions
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Your RSVP',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _RsvpButton(
                      label: 'Attending',
                      icon: Icons.check_circle_outline,
                      isSelected: detail.rsvpSummary['attending'] != null,
                      onPressed: () => _handleRsvp(ref, 'attending'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _RsvpButton(
                      label: 'Maybe',
                      icon: Icons.schedule_outlined,
                      isSelected: detail.rsvpSummary['pending'] != null,
                      onPressed: () => _handleRsvp(ref, 'pending'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _RsvpButton(
                      label: 'Decline',
                      icon: Icons.cancel_outlined,
                      isSelected: detail.rsvpSummary['declined'] != null,
                      onPressed: () => _handleRsvp(ref, 'declined'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        // Attendee list
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text(
                    'Attendees',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w600,
                          color: AppColors.textPrimary,
                        ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 2,
                    ),
                    decoration: BoxDecoration(
                      color: AppColors.accentSecondary.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      '${detail.attendeeCount}',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.accentSecondary,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              rsvpsAsync.when(
                loading: () => const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                ),
                error: (err, _) => Padding(
                  padding: const EdgeInsets.all(24),
                  child: Center(
                    child: Text(
                      'Failed to load RSVPs',
                      style: TextStyle(color: AppColors.textMuted),
                    ),
                  ),
                ),
                data: (rsvps) {
                  if (rsvps.items.isEmpty) {
                    return Padding(
                      padding: const EdgeInsets.all(24),
                      child: Center(
                        child: Text(
                          'No RSVPs yet',
                          style: TextStyle(color: AppColors.textMuted),
                        ),
                      ),
                    );
                  }
                  return Column(
                    children: rsvps.items.map((rsvp) {
                      return ListTile(
                        dense: true,
                        contentPadding: EdgeInsets.zero,
                        leading: CircleAvatar(
                          radius: 16,
                          backgroundColor:
                              AppColors.accentPrimary.withValues(alpha: 0.15),
                          child: Icon(
                            Icons.person,
                            size: 18,
                            color: AppColors.accentPrimary,
                          ),
                        ),
                        title: Text(
                          rsvp.userId,
                          style: TextStyle(
                            fontSize: 14,
                            color: AppColors.textPrimary,
                          ),
                        ),
                        trailing: _rsvpStatusChip(rsvp.status),
                      );
                    }).toList(),
                  );
                },
              ),
            ],
          ),
        ),

        const SizedBox(height: 32),
      ],
    );
  }

  void _handleRsvp(WidgetRef ref, String status) {
    ref.read(rsvpNotifierProvider.notifier).rsvp(
          partyId: partyId,
          status: status,
        );
  }

  Widget _rsvpStatusChip(String status) {
    Color color;
    switch (status) {
      case 'attending':
        color = AppColors.success;
      case 'pending':
        color = AppColors.warning;
      case 'declined':
        color = AppColors.destructive;
      default:
        color = AppColors.textMuted;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        status[0].toUpperCase() + status.substring(1),
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }
}

// --- Sub-widgets ---

class _StatusBadge extends StatelessWidget {
  final String status;

  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    String label;
    switch (status) {
      case 'live':
        color = AppColors.success;
        label = '● LIVE';
      case 'scheduled':
        color = AppColors.accentSecondary;
        label = '● SCHEDULED';
      case 'completed':
        color = AppColors.textMuted;
        label = '● COMPLETED';
      case 'cancelled':
        color = AppColors.destructive;
        label = '● CANCELLED';
      default:
        color = AppColors.textMuted;
        label = status.toUpperCase();
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: color,
          letterSpacing: 0.5,
        ),
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _InfoRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: AppColors.accentPrimary),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: AppColors.textMuted,
                  letterSpacing: 0.3,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  color: AppColors.textPrimary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _RsvpButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onPressed;

  const _RsvpButton({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected
            ? AppColors.accentPrimary.withValues(alpha: 0.2)
            : Colors.white.withValues(alpha: 0.06),
        foregroundColor: isSelected ? AppColors.accentPrimary : Colors.white70,
        padding: const EdgeInsets.symmetric(vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: BorderSide(
            color: isSelected
                ? AppColors.accentPrimary.withValues(alpha: 0.4)
                : Colors.white.withValues(alpha: 0.1),
          ),
        ),
        textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 20),
          const SizedBox(height: 4),
          Text(label),
        ],
      ),
    );
  }
}
