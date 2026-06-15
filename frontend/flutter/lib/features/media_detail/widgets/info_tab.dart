import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/media_detail/models/media_detail.dart';

class InfoTab extends StatelessWidget {
  final MediaDetail media;

  const InfoTab({super.key, required this.media});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Synopsis
          if (media.synopsis != null && media.synopsis!.isNotEmpty) ...[
            const Text('Synopsis', style: TextStyle(
              color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(
              media.synopsis!,
              style: const TextStyle(color: AppColors.textSecondary, fontSize: 14, height: 1.5),
            ),
            const SizedBox(height: 20),
          ],

          // Details
          const Text('Details', style: TextStyle(
            color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          _detailRow('Type', media.mediaType.toUpperCase()),
          if (media.format != null) _detailRow('Format', media.format!),
          if (media.episodeCount != null) _detailRow('Episodes', '${media.episodeCount}'),
          if (media.chapterCount != null) _detailRow('Chapters', '${media.chapterCount}'),
          if (media.volumeCount != null) _detailRow('Volumes', '${media.volumeCount}'),
          if (media.durationMinutes != null) _detailRow('Duration', '${media.durationMinutes} min/ep'),
          if (media.season != null && media.seasonYear != null)
            _detailRow('Season', '${_capitalize(media.season!)} ${media.seasonYear}'),
          if (media.averageScore != null)
            _detailRow('Score', media.averageScore!.toStringAsFixed(1)),
          if (media.popularity != null) _detailRow('Popularity', '#${media.popularity}'),
          if (media.status.isNotEmpty) _detailRow('Status', _formatStatus(media.status)),
          if (media.startDate != null) _detailRow('Start', media.startDate!),
          if (media.endDate != null) _detailRow('End', media.endDate!),
          if (media.countryOfOrigin != null) _detailRow('Country', _countryName(media.countryOfOrigin!)),
          if (media.isAdult)
            _detailRow('Mature', '18+', highlight: true),

          // Genres
          if (media.genres != null && media.genres!.isNotEmpty) ...[
            const SizedBox(height: 20),
            const Text('Genres', style: TextStyle(
              color: AppColors.textPrimary, fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: media.genres!.map((g) => _genreChip(g.name)).toList(),
            ),
          ],
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _detailRow(String label, String value, {bool highlight = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: const TextStyle(color: AppColors.textMuted, fontSize: 13),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: highlight ? AppColors.warning : AppColors.textPrimary,
                fontSize: 13,
                fontWeight: highlight ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _genreChip(String name) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.accentPrimary.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        name,
        style: const TextStyle(color: AppColors.accentPrimary, fontSize: 12),
      ),
    );
  }

  String _capitalize(String s) {
    if (s.isEmpty) return s;
    return s[0].toUpperCase() + s.substring(1);
  }

  String _formatStatus(String status) {
    return status.replaceAll('_', ' ').split(' ').map((w) => _capitalize(w)).join(' ');
  }

  String _countryName(String code) {
    switch (code.toUpperCase()) {
      case 'JP': return 'Japan';
      case 'KR': return 'South Korea';
      case 'CN': return 'China';
      default: return code;
    }
  }
}
