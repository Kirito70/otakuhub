import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/media_detail/models/media_detail.dart';

class EpisodesTab extends StatelessWidget {
  final List<EpisodeInfo> episodes;

  const EpisodesTab({super.key, required this.episodes});

  @override
  Widget build(BuildContext context) {
    if (episodes.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.videocam_off_outlined, size: 48, color: AppColors.textMuted),
            SizedBox(height: 8),
            Text('No episode data available', style: TextStyle(color: AppColors.textSecondary)),
          ],
        ),
      );
    }

    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: episodes.length,
      separatorBuilder: (_, __) => const Divider(height: 1, color: AppColors.borderDefault),
      itemBuilder: (context, index) {
        final ep = episodes[index];
        final aired = ep.airDate != null;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Row(
            children: [
              // Thumbnail
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: SizedBox(
                  width: 120,
                  height: 68,
                  child: ep.thumbnailUrl != null
                      ? Image.network(
                          ep.thumbnailUrl!,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => _placeholderThumb(),
                          loadingBuilder: (_, child, progress) {
                            if (progress == null) return child;
                            return _placeholderThumb();
                          },
                        )
                      : _placeholderThumb(),
                ),
              ),
              const SizedBox(width: 12),
              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ep. ${ep.episodeNumber}',
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    if (ep.title != null) ...[
                      const SizedBox(height: 2),
                      Text(
                        ep.title!,
                        style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        if (ep.durationMinutes != null)
                          Padding(
                            padding: const EdgeInsets.only(right: 12),
                            child: Text(
                              '${ep.durationMinutes}m',
                              style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
                            ),
                          ),
                        if (aired)
                          Text(
                            _formatDate(ep.airDate!),
                            style: TextStyle(
                              color: aired ? AppColors.textMuted : AppColors.warning,
                              fontSize: 12,
                            ),
                          ),
                        if (!aired)
                          const Text(
                            'TBA',
                            style: TextStyle(color: AppColors.warning, fontSize: 12),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _placeholderThumb() {
    return Container(
      color: AppColors.bgElevated,
      child: const Center(child: Icon(Icons.movie_outlined, color: AppColors.textMuted, size: 20)),
    );
  }

  String _formatDate(String date) {
    if (date.length >= 10) {
      return date.substring(0, 10);
    }
    return date;
  }
}
