import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';

class HeroBanner extends StatelessWidget {
  final String title;
  final String? bannerImage;
  final String? coverImage;
  final double? score;
  final String? year;
  final String mediaType;
  final String? format;
  final String status;
  final int? episodeCount;
  final List<String>? genres;
  final VoidCallback? onPlay;
  final VoidCallback? onAddToList;

  const HeroBanner({
    super.key,
    required this.title,
    this.bannerImage,
    this.coverImage,
    this.score,
    this.year,
    required this.mediaType,
    this.format,
    this.status = 'not_yet_released',
    this.episodeCount,
    this.genres,
    this.onPlay,
    this.onAddToList,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 280,
      child: Stack(
        children: [
          // Banner image
          Positioned.fill(
            child: _buildBanner(),
          ),
          // Gradient overlay
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.transparent,
                    Colors.transparent,
                    AppColors.bgPrimary,
                  ],
                ),
              ),
            ),
          ),
          // Content
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  // Small cover thumbnail
                  ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: SizedBox(
                      width: 80,
                      height: 120,
                      child: _buildCoverThumb(),
                    ),
                  ),
                  const SizedBox(width: 16),
                  // Info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          title,
                          style: const TextStyle(
                            color: AppColors.textPrimary,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            _metaChip(mediaType.toUpperCase(), AppColors.accentPrimary),
                            if (format != null) ...[
                              const SizedBox(width: 6),
                              _metaChip(format!, AppColors.accentSecondary),
                            ],
                            if (year != null) ...[
                              const SizedBox(width: 6),
                              Text(year!, style: const TextStyle(
                                color: AppColors.textSecondary, fontSize: 12)),
                            ],
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            // Score
                            if (score != null) ...[
                              const Icon(Icons.star, size: 16, color: Color(0xFFF59E0B)),
                              const SizedBox(width: 4),
                              Text(
                                score!.toStringAsFixed(1),
                                style: const TextStyle(
                                  color: AppColors.textPrimary,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                              const SizedBox(width: 12),
                            ],
                            // Status
                            Text(
                              status.replaceAll('_', ' '),
                              style: TextStyle(
                                color: _statusColor(status),
                                fontSize: 12,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            if (episodeCount != null) ...[
                              const SizedBox(width: 12),
                              Text(
                                '$episodeCount eps',
                                style: const TextStyle(
                                  color: AppColors.textSecondary, fontSize: 12),
                              ),
                            ],
                          ],
                        ),
                        const SizedBox(height: 8),
                        // Action buttons
                        Row(
                          children: [
                            if (onPlay != null)
                              ElevatedButton.icon(
                                onPressed: onPlay,
                                icon: const Icon(Icons.play_arrow, size: 18),
                                label: const Text('Play'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.accentPrimary,
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(horizontal: 16),
                                  minimumSize: Size.zero,
                                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                ),
                              ),
                            if (onPlay != null && onAddToList != null)
                              const SizedBox(width: 8),
                            if (onAddToList != null)
                              OutlinedButton.icon(
                                onPressed: onAddToList,
                                icon: const Icon(Icons.add, size: 18),
                                label: const Text('Add to List'),
                                style: OutlinedButton.styleFrom(
                                  foregroundColor: AppColors.accentPrimary,
                                  side: const BorderSide(color: AppColors.accentPrimary),
                                  padding: const EdgeInsets.symmetric(horizontal: 16),
                                  minimumSize: Size.zero,
                                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                ),
                              ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBanner() {
    if (bannerImage == null && coverImage == null) {
      return Container(color: AppColors.bgSecondary);
    }
    return Image.network(
      bannerImage ?? coverImage!,
      fit: BoxFit.cover,
      errorBuilder: (_, __, ___) => Container(color: AppColors.bgSecondary),
      loadingBuilder: (_, child, progress) {
        if (progress == null) return child;
        return Container(color: AppColors.bgElevated);
      },
    );
  }

  Widget _buildCoverThumb() {
    if (coverImage == null) {
      return Container(
        color: AppColors.bgElevated,
        child: const Icon(Icons.movie_outlined, color: AppColors.textMuted, size: 24),
      );
    }
    return Image.network(
      coverImage!,
      fit: BoxFit.cover,
      errorBuilder: (_, __, ___) => Container(
        color: AppColors.bgElevated,
        child: const Icon(Icons.broken_image, color: AppColors.textMuted),
      ),
    );
  }

  Widget _metaChip(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'releasing':
        return AppColors.success;
      case 'finished':
        return AppColors.textSecondary;
      case 'not_yet_released':
        return AppColors.warning;
      case 'cancelled':
        return AppColors.destructive;
      case 'hiatus':
        return AppColors.warning;
      default:
        return AppColors.textSecondary;
    }
  }
}
