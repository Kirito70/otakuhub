import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/tracking/models/airing_item.dart';
import 'package:otakuhub/features/tracking/providers/airing_calendar_provider.dart';

class AiringCalendarScreen extends ConsumerWidget {
  const AiringCalendarScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final airingAsync = ref.watch(airingScheduleProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Airing Calendar'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh',
            onPressed: () => ref.invalidate(airingScheduleProvider),
          ),
        ],
      ),
      body: airingAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => _buildError(context, ref, err),
        data: (data) => _buildContent(context, data),
      ),
    );
  }

  Widget _buildError(BuildContext context, WidgetRef ref, Object err) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 64, color: AppColors.destructive),
            const SizedBox(height: 16),
            Text(
              'Failed to load airing schedule',
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            if (err.toString().isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(
                err.toString(),
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textMuted,
                    ),
                textAlign: TextAlign.center,
              ),
            ],
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: () => ref.invalidate(airingScheduleProvider),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context, AiringResponse data) {
    final items = data.items;

    if (items.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.event_busy, size: 64, color: AppColors.textMuted),
              const SizedBox(height: 16),
              Text(
                'No upcoming airings',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(
                'Check back later for new episode releases.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    // Group items by date
    final grouped = <String, List<AiringEpisodeItem>>{};
    for (final item in items) {
      final dateKey = _formatDateKey(item.airDate);
      grouped.putIfAbsent(dateKey, () => []);
      grouped[dateKey]!.add(item);
    }

    // Sort dates
    final sortedDates = grouped.keys.toList()..sort();

    return ListView.builder(
      padding: const EdgeInsets.symmetric(vertical: 8),
      itemCount: sortedDates.length,
      itemBuilder: (context, index) {
        final dateKey = sortedDates[index];
        final dateItems = grouped[dateKey]!;
        return _DateGroup(
          dateKey: dateKey,
          items: dateItems,
        );
      },
    );
  }

  String _formatDateKey(String? airDate) {
    if (airDate == null || airDate.isEmpty) return 'Unknown date';
    // air_date comes as ISO datetime string like "2026-06-20T12:00:00Z"
    // Extract just the date part
    if (airDate.length >= 10) {
      return airDate.substring(0, 10);
    }
    return airDate;
  }
}

class _DateGroup extends StatelessWidget {
  final String dateKey;
  final List<AiringEpisodeItem> items;

  const _DateGroup({
    required this.dateKey,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    final isToday = dateKey == _todayDateKey();
    final isTomorrow = dateKey == _tomorrowDateKey();

    String label;
    if (isToday) {
      label = 'Today';
    } else if (isTomorrow) {
      label = 'Tomorrow';
    } else {
      // Format as readable date
      final parts = dateKey.split('-');
      if (parts.length == 3) {
        final months = [
          'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ];
        final month = int.tryParse(parts[1]) ?? 1;
        final day = int.tryParse(parts[2]) ?? 1;
        final year = parts[0];
        label = '${months[month - 1]} $day, $year';
      } else {
        label = dateKey;
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Row(
            children: [
              Container(
                width: 4,
                height: 20,
                decoration: BoxDecoration(
                  color: isToday ? AppColors.accentPrimary : AppColors.accentSecondary,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(width: 12),
              Text(
                label,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isToday ? AppColors.accentPrimary : null,
                    ),
              ),
              const SizedBox(width: 8),
              Text(
                '(${items.length} episode${items.length != 1 ? 's' : ''})',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: AppColors.textMuted,
                    ),
              ),
            ],
          ),
        ),
        ...items.map((item) => _AiringEpisodeTile(item: item)),
      ],
    );
  }

  String _todayDateKey() {
    final now = DateTime.now();
    return '${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}';
  }

  String _tomorrowDateKey() {
    final tomorrow = DateTime.now().add(const Duration(days: 1));
    return '${tomorrow.year}-${tomorrow.month.toString().padLeft(2, '0')}-${tomorrow.day.toString().padLeft(2, '0')}';
  }
}

class _AiringEpisodeTile extends StatelessWidget {
  final AiringEpisodeItem item;

  const _AiringEpisodeTile({required this.item});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: ClipRRect(
        borderRadius: BorderRadius.circular(4),
        child: SizedBox(
          width: 48,
          height: 64,
          child: item.mediaCover != null && item.mediaCover!.isNotEmpty
              ? Image.network(
                  item.mediaCover!,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    color: AppColors.bgElevated,
                    child: const Icon(Icons.broken_image, color: AppColors.textMuted),
                  ),
                )
              : Container(
                  color: AppColors.bgElevated,
                  child: const Icon(Icons.movie, color: AppColors.textMuted),
                ),
        ),
      ),
      title: Text(
        item.mediaTitle,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w500,
            ),
      ),
      subtitle: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 2),
          Text(
            'Ep ${item.episodeNumber}${item.title != null && item.title!.isNotEmpty ? ' — ${item.title}' : ''}',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
          if (item.airDate != null && item.airDate!.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(
              _formatTime(item.airDate!),
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: AppColors.textMuted,
                  ),
            ),
          ],
        ],
      ),
      trailing: item.durationMinutes != null
          ? Text(
              '${item.durationMinutes}m',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: AppColors.textMuted,
                  ),
            )
          : null,
      onTap: () {
        context.pushNamed(
          RouteNames.mediaDetail,
          pathParameters: {'id': item.mediaId},
        );
      },
    );
  }

  String _formatTime(String airDate) {
    try {
      // Parse ISO datetime and extract time portion
      if (airDate.contains('T')) {
        final timePart = airDate.split('T')[1];
        // Take just HH:MM
        if (timePart.length >= 5) {
          return timePart.substring(0, 5);
        }
      }
    } catch (_) {}
    return airDate;
  }
}
