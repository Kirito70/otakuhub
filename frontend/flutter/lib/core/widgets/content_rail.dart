import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';
import 'package:otakuhub/core/widgets/poster_card.dart';
import 'package:otakuhub/core/widgets/section_header.dart';

/// ADR 094 — ContentRail: horizontal scrollable row of poster cards.
///
/// SectionHeader at top, snap-to-card PosterCards with edge gradient fade.
class ContentRail extends StatelessWidget {
  final String title;
  final String? seeAllLabel;
  final VoidCallback? onSeeAll;
  final bool showAccentBar;
  final List<_ContentRailItem> items;
  final double cardWidth;
  final double height;

  const ContentRail({
    super.key,
    required this.title,
    this.seeAllLabel,
    this.onSeeAll,
    this.showAccentBar = false,
    required this.items,
    this.cardWidth = 140,
    this.height = 240,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        SectionHeader(
          title: title,
          seeAllLabel: seeAllLabel,
          onSeeAll: onSeeAll,
          showAccentBar: showAccentBar,
        ),
        SizedBox(
          height: height,
          child: Stack(
            children: [
              // Scrollable cards
              ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: EdgeInsets.only(
                  left: tokens.spaceMd,
                  right: tokens.spaceLg + 24, // extra for fade
                ),
                itemCount: items.length,
                itemExtent: cardWidth + 12, // card width + gap
                itemBuilder: (context, index) {
                  final item = items[index];
                  return Padding(
                    padding: const EdgeInsets.only(right: 12),
                    child: PosterCard(
                      imageUrl: item.imageUrl,
                      title: item.title,
                      format: item.format,
                      seasonYear: item.seasonYear,
                      score: item.score,
                      status: item.status,
                      progress: item.progress,
                      maxProgress: item.maxProgress,
                      width: cardWidth,
                      onTap: item.onTap,
                      onLongPress: item.onLongPress,
                      onQuickAction: item.onQuickAction,
                    ),
                  );
                },
              ),
              // Right edge fade
              IgnorePointer(
                child: Container(
                  width: 48,
                  height: height,
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      begin: Alignment.centerLeft,
                      end: Alignment.centerRight,
                      colors: [
                        Colors.transparent,
                        tokens.bgBase.withValues(alpha: 0.85),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// Data model for a single content rail item.
class _ContentRailItem {
  final String imageUrl;
  final String? title;
  final String? format;
  final int? seasonYear;
  final double? score;
  final String? status;
  final int? progress;
  final int? maxProgress;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final VoidCallback? onQuickAction;

  const _ContentRailItem({
    required this.imageUrl,
    this.title,
    this.format,
    this.seasonYear,
    this.score,
    this.status,
    this.progress,
    this.maxProgress,
    this.onTap,
    this.onLongPress,
    this.onQuickAction,
  });
}

/// Convenience constructor for ContentRail items.
ContentRailItem contentRailItem({
  required String imageUrl,
  String? title,
  String? format,
  int? seasonYear,
  double? score,
  String? status,
  int? progress,
  int? maxProgress,
  VoidCallback? onTap,
  VoidCallback? onLongPress,
  VoidCallback? onQuickAction,
}) {
  return ContentRailItem._(
    imageUrl: imageUrl,
    title: title,
    format: format,
    seasonYear: seasonYear,
    score: score,
    status: status,
    progress: progress,
    maxProgress: maxProgress,
    onTap: onTap,
    onLongPress: onLongPress,
    onQuickAction: onQuickAction,
  );
}

class ContentRailItem {
  final String imageUrl;
  final String? title;
  final String? format;
  final int? seasonYear;
  final double? score;
  final String? status;
  final int? progress;
  final int? maxProgress;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final VoidCallback? onQuickAction;

  const ContentRailItem({
    required this.imageUrl,
    this.title,
    this.format,
    this.seasonYear,
    this.score,
    this.status,
    this.progress,
    this.maxProgress,
    this.onTap,
    this.onLongPress,
    this.onQuickAction,
  });

  ContentRailItem._({
    required this.imageUrl,
    this.title,
    this.format,
    this.seasonYear,
    this.score,
    this.status,
    this.progress,
    this.maxProgress,
    this.onTap,
    this.onLongPress,
    this.onQuickAction,
  });
}
