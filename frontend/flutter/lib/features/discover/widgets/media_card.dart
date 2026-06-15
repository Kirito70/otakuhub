import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/discover/models/media_item.dart';

class MediaCard extends StatelessWidget {
  final MediaItem item;
  final double? progressPercent;
  final bool showBadges;
  final double height;

  const MediaCard({
    super.key,
    required this.item,
    this.progressPercent,
    this.showBadges = true,
    this.height = 260,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => context.push('/media/${item.id}'),
      child: Container(
        height: height,
        decoration: BoxDecoration(
          color: AppColors.bgSecondary,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.borderDefault),
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Cover image
            Expanded(
              child: Stack(
                fit: StackFit.expand,
                children: [
                  _buildCoverImage(),
                  // Badges
                  if (showBadges) _buildBadges(),
                  // Progress bar
                  if (progressPercent != null && progressPercent! > 0)
                    Positioned(
                      bottom: 0,
                      left: 0,
                      right: 0,
                      child: LinearProgressIndicator(
                        value: progressPercent!.clamp(0.0, 1.0),
                        backgroundColor: Colors.white.withValues(alpha: 0.2),
                        color: AppColors.accentPrimary,
                        minHeight: 3,
                      ),
                    ),
                ],
              ),
            ),
            // Info
            Padding(
              padding: const EdgeInsets.all(8),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.displayTitle,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      if (item.averageScore != null) ...[
                        const Icon(Icons.star, size: 12, color: Color(0xFFF59E0B)),
                        const SizedBox(width: 2),
                        Text(
                          item.averageScore!.toStringAsFixed(1),
                          style: const TextStyle(
                            color: AppColors.textSecondary,
                            fontSize: 11,
                          ),
                        ),
                        const SizedBox(width: 8),
                      ],
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                        decoration: BoxDecoration(
                          color: AppColors.accentSecondary.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(3),
                        ),
                        child: Text(
                          _shortType(item.mediaType),
                          style: const TextStyle(
                            color: AppColors.accentSecondary,
                            fontSize: 9,
                            fontWeight: FontWeight.w600,
                          ),
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
    );
  }

  Widget _buildCoverImage() {
    final cover = item.coverImageMedium ?? item.coverImageLarge;
    if (cover == null) {
      return Container(
        color: AppColors.bgElevated,
        child: const Center(
          child: Icon(Icons.movie_outlined, color: AppColors.textMuted, size: 32),
        ),
      );
    }
    return Image.network(
      cover,
      fit: BoxFit.cover,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return Container(
          color: AppColors.bgElevated,
          child: const Center(
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
        );
      },
      errorBuilder: (context, error, stackTrace) {
        return Container(
          color: AppColors.bgElevated,
          child: const Center(
            child: Icon(Icons.broken_image_outlined, color: AppColors.textMuted, size: 32),
          ),
        );
      },
    );
  }

  Widget _buildBadges() {
    return Positioned(
      top: 6,
      left: 6,
      child: Row(
        children: [
          _badge(item.mediaType.toUpperCase(), AppColors.accentPrimary),
          if (item.format != null && item.format!.length <= 8)
            const SizedBox(width: 4),
          if (item.format != null && item.format!.length <= 8)
            _badge(item.format!, AppColors.accentSecondary),
        ],
      ),
    );
  }

  Widget _badge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.85),
        borderRadius: BorderRadius.circular(3),
      ),
      child: Text(
        text,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 9,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  String _shortType(String type) {
    if (type == 'light_novel') return 'LN';
    if (type == 'one_shot') return 'OS';
    return type.substring(0, 1).toUpperCase();
  }
}
