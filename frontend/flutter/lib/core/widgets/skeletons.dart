import 'package:flutter/material.dart';
import 'package:shimmer/shimmer.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — Skeleton loaders for the app.
///
/// Uses shimmer package with bgPrimary → bgSurfaceAlt wave.
class AppSkeleton {
  AppSkeleton._();

  static Shimmer _base({
  required Widget child,
  }) =>
      Shimmer.fromColors(
        baseColor: const Color(0xFF1A1A1A),
        highlightColor: const Color(0xFF2A2A2A),
        period: const Duration(milliseconds: 1600),
        child: child,
      );

  /// Poster card skeleton
  static Widget poster({double width = 140}) {
    return _base(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: width,
            height: width * 1.5,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
            ),
          ),
          const SizedBox(height: 6),
          Container(
            width: width * 0.6,
            height: 12,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
        ],
      ),
    );
  }

  /// Content rail skeleton
  static Widget rail({int count = 5, double cardWidth = 140}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        _sectionHeaderSkeleton(),
        const SizedBox(height: 8),
        SizedBox(
          height: cardWidth * 1.5 + 20,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.only(left: 16),
            itemCount: count,
            itemExtent: cardWidth + 12,
            itemBuilder: (_, __) => Padding(
              padding: const EdgeInsets.only(right: 12),
              child: poster(width: cardWidth),
            ),
          ),
        ),
      ],
    );
  }

  /// List tile skeleton
  static Widget listTile() {
    return _base(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    height: 14,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    height: 11,
                    width: 120,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Media detail skeleton
  static Widget mediaDetail() {
    return _base(
      child: Column(
        children: [
          // Banner area
          Container(
            height: 240,
            color: Colors.white,
          ),
          const SizedBox(height: 16),
          // Poster row
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Container(
                  width: 120,
                  height: 180,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(height: 18, color: Colors.white),
                      const SizedBox(height: 8),
                      Container(height: 14, width: 140, color: Colors.white),
                      const SizedBox(height: 8),
                      Container(height: 14, width: 100, color: Colors.white),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Text line skeleton
  static Widget textLine({double width = double.infinity, double height = 14}) {
    return _base(
      child: Container(
        height: height,
        width: width,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(4),
        ),
      ),
    );
  }

  static Widget _sectionHeaderSkeleton() {
    return _base(
      child: Padding(
        padding: const EdgeInsets.only(left: 16, right: 16, bottom: 8),
        child: Row(
          children: [
            Container(
              height: 20,
              width: 160,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            const Spacer(),
            Container(
              height: 14,
              width: 60,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
