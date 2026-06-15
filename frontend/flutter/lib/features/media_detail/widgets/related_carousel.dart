import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:otakuhub/core/router/route_names.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/media_detail/models/media_detail.dart';

class RelatedCarousel extends StatelessWidget {
  final List<MediaRelation> relations;

  const RelatedCarousel({super.key, required this.relations});

  @override
  Widget build(BuildContext context) {
    if (relations.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.link_off, size: 48, color: AppColors.textMuted),
            SizedBox(height: 8),
            Text('No related media', style: TextStyle(color: AppColors.textSecondary)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      scrollDirection: Axis.horizontal,
      itemCount: relations.length,
      itemBuilder: (context, index) {
        final rel = relations[index];
        return GestureDetector(
          onTap: () {
            context.goNamed(RouteNames.mediaDetail, pathParameters: {'id': rel.id});
          },
          child: Container(
            width: 130,
            margin: const EdgeInsets.only(right: 10),
            decoration: BoxDecoration(
              color: AppColors.bgSecondary,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppColors.borderDefault),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Cover
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(7)),
                  child: SizedBox(
                    width: 130,
                    height: 180,
                    child: rel.coverImageMedium != null
                        ? Image.network(
                            rel.coverImageMedium!,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => _placeholder(),
                            loadingBuilder: (_, child, progress) {
                              if (progress == null) return child;
                              return _placeholder();
                            },
                          )
                        : _placeholder(),
                  ),
                ),
                // Info
                Padding(
                  padding: const EdgeInsets.all(6),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        rel.displayTitle,
                        style: const TextStyle(
                          color: AppColors.textPrimary, fontSize: 12, fontWeight: FontWeight.w500),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          _relationBadge(rel.relationType),
                          const SizedBox(width: 4),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                            decoration: BoxDecoration(
                              color: AppColors.accentSecondary.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(3),
                            ),
                            child: Text(
                              (rel.mediaType ?? 'UNKNOWN').toUpperCase(),
                              style: const TextStyle(
                                color: AppColors.accentSecondary, fontSize: 9, fontWeight: FontWeight.bold),
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
      },
    );
  }

  Widget _placeholder() {
    return Container(
      color: AppColors.bgElevated,
      child: const Center(child: Icon(Icons.movie_outlined, color: AppColors.textMuted, size: 32)),
    );
  }

  Widget _relationBadge(String type) {
    final label = type.replaceAll('_', ' ');
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
      decoration: BoxDecoration(
        color: AppColors.accentPrimary.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(3),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: AppColors.accentPrimary, fontSize: 9, fontWeight: FontWeight.bold),
      ),
    );
  }
}
