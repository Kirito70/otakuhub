import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';
import 'package:otakuhub/core/widgets/score_chip.dart';

/// ADR 094 — PosterCard: the atomic visual unit of the app.
///
/// Sizes: sm (w104), md (w140), lg (w168). 2:3 aspect ratio.
/// Resting: image + ScoreChip + thin status rail.
/// Hover (pointer): dark scrim + title + format/year + quick-action button.
/// Long-press: triggers onLongPress callback (opens QuickActionSheet).
class PosterCard extends StatefulWidget {
  final String imageUrl;
  final String? title;
  final String? format;
  final int? seasonYear;
  final double? score;
  final String? status;
  final int? progress;
  final int? maxProgress;
  final double width;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final VoidCallback? onQuickAction;

  const PosterCard({
    super.key,
    required this.imageUrl,
    this.title,
    this.format,
    this.seasonYear,
    this.score,
    this.status,
    this.progress,
    this.maxProgress,
    this.width = 140,
    this.onTap,
    this.onLongPress,
    this.onQuickAction,
  });

  @override
  State<PosterCard> createState() => _PosterCardState();
}

class _PosterCardState extends State<PosterCard> {
  bool _isHovered = false;

  static final _sizes = <double>{104, 140, 168};

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final width = _sizes.contains(widget.width) ? widget.width : 140.0;
    final height = width * 1.5; // 2:3 aspect ratio

    return SizedBox(
      width: width,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Poster image
          GestureDetector(
            onTap: widget.onTap,
            onLongPress: widget.onLongPress,
            child: MouseRegion(
              onEnter: (_) => setState(() => _isHovered = true),
              onExit: (_) => setState(() => _isHovered = false),
              child: SizedBox(
                width: width,
                height: height,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(tokens.radiusMd),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      // Image
                      CachedNetworkImage(
                        imageUrl: widget.imageUrl,
                        fit: BoxFit.cover,
                        placeholder: (_, __) => Container(
                          color: tokens.bgSurfaceAlt,
                        ),
                        errorWidget: (_, __, ___) => Container(
                          color: tokens.bgSurfaceAlt,
                          child: Center(
                            child: Icon(
                              Icons.movie_outlined,
                              color: tokens.textTertiary,
                              size: 28,
                            ),
                          ),
                        ),
                      ),
                      // Inner border
                      Positioned.fill(
                        child: IgnorePointer(
                          child: Container(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(tokens.radiusMd),
                              border: Border.all(color: tokens.borderSubtle, width: 0.5),
                            ),
                          ),
                        ),
                      ),
                      // Score chip (top-right)
                      if (widget.score != null || widget.score == null)
                        Positioned(
                          top: 6,
                          right: 6,
                          child: ScoreChip(
                            score: widget.score,
                            size: width > 120 ? 48 : 40,
                            compact: width <= 120,
                          ),
                        ),
                      // Status rail (bottom, 3px)
                      if (widget.status != null)
                        Positioned(
                          bottom: 0,
                          left: 0,
                          right: 0,
                          child: Container(
                            height: 3,
                            decoration: BoxDecoration(
                              color: tokens.statusColor(widget.status!),
                              borderRadius: const BorderRadius.vertical(
                                bottom: Radius.circular(14),
                              ),
                            ),
                          ),
                        ),
                      // Hover overlay (pointer only)
                      if (_isHovered)
                        Positioned.fill(
                          child: Container(
                            decoration: BoxDecoration(
                              borderRadius: BorderRadius.circular(tokens.radiusMd),
                              gradient: LinearGradient(
                                begin: Alignment.bottomCenter,
                                end: Alignment.topCenter,
                                colors: [
                                  Colors.black.withValues(alpha: 0.85),
                                  Colors.transparent,
                                ],
                              ),
                            ),
                            padding: const EdgeInsets.all(10),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.end,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                if (widget.title != null)
                                  Text(
                                    widget.title!,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: TextStyle(
                                      fontFamily: 'Plus Jakarta Sans',
                                      fontSize: width > 120 ? 15 : 13,
                                      fontWeight: FontWeight.w600,
                                      height: 1.2,
                                      color: tokens.textPrimary,
                                    ),
                                  ),
                                const SizedBox(height: 2),
                                if (widget.format != null || widget.seasonYear != null)
                                  Text(
                                    [
                                      if (widget.format != null) widget.format!,
                                      if (widget.seasonYear != null) '${widget.seasonYear}',
                                    ].join(' · '),
                                    style: TextStyle(
                                      fontFamily: 'Plus Jakarta Sans',
                                      fontSize: 11,
                                      color: tokens.textSecondary,
                                      height: 1.2,
                                    ),
                                  ),
                                const SizedBox(height: 6),
                                // Quick-action button
                                InkWell(
                                  onTap: widget.onQuickAction,
                                  borderRadius: BorderRadius.circular(tokens.radiusPill),
                                  child: Container(
                                    width: 28,
                                    height: 28,
                                    decoration: BoxDecoration(
                                      color: tokens.accentPrimary,
                                      shape: BoxShape.circle,
                                    ),
                                    child: Icon(
                                      Icons.add_rounded,
                                      size: 18,
                                      color: tokens.textOnAccent,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),
          ),
          // Progress bar
          if (widget.progress != null && widget.maxProgress != null && widget.maxProgress! > 0)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(2),
                child: LinearProgressIndicator(
                  value: widget.progress! / widget.maxProgress!,
                  backgroundColor: tokens.bgSurfaceAlt,
                  valueColor: AlwaysStoppedAnimation(tokens.accentMint),
                  minHeight: 2,
                ),
              ),
            ),
        ],
      ),
    );
  }
}
