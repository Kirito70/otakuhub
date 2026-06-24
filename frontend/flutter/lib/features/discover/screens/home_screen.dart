import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:cached_network_image/cached_network_image.dart';

import 'package:otakuhub/core/theme/app_tokens.dart';
import 'package:otakuhub/core/widgets/app_button.dart';
import 'package:otakuhub/core/widgets/app_empty_state.dart';
import 'package:otakuhub/core/widgets/poster_card.dart';
import 'package:otakuhub/core/widgets/score_chip.dart';
import 'package:otakuhub/core/widgets/skeletons.dart';
import 'package:otakuhub/core/widgets/status_pill.dart';
import 'package:otakuhub/features/discover/providers/home_provider.dart';
import 'package:otakuhub/features/discover/models/home_data.dart';

/// Home screen — genre-based browse layout.
///
/// Shows a hero spotlight at top, then media type sections (Anime / Manga / Manhwa)
/// each with genre-based horizontal rails.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  late PageController _pageController;
  Timer? _autoCycleTimer;
  int _currentSpotlight = 0;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();
    _startAutoCycle();
  }

  @override
  void dispose() {
    _pageController.dispose();
    _autoCycleTimer?.cancel();
    super.dispose();
  }

  void _startAutoCycle() {
    _autoCycleTimer?.cancel();
    _autoCycleTimer = Timer.periodic(const Duration(seconds: 8), (_) {
      final homeData = ref.read(homeProvider).asData?.value;
      if (homeData == null || homeData.spotlight.length <= 1) return;
      final next = (_currentSpotlight + 1) % homeData.spotlight.length;
      _pageController.animateToPage(
        next,
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeOutCubic,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final homeAsync = ref.watch(homeProvider);

    return Scaffold(
      body: homeAsync.when(
        loading: () => const _HomeSkeleton(),
        error: (error, _) => Center(
          child: AppEmptyState.error(
            message: 'Could not load your home feed',
            onAction: () => ref.invalidate(homeProvider),
          ),
        ),
        data: (homeData) {
          if (homeData.isEmpty) {
            return const Center(
              child: AppEmptyState(
                icon: Icons.explore_outlined,
                message:
                    'No media data yet. Seed the database to populate your home page.',
              ),
            );
          }
          return _HomeContent(
            homeData: homeData,
            onRefresh: () => ref.invalidate(homeProvider),
            onSpotlightPageChanged: (index) {
              setState(() => _currentSpotlight = index);
              _startAutoCycle();
            },
          );
        },
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Content
// ---------------------------------------------------------------------------
class _HomeContent extends ConsumerWidget {
  final HomeData homeData;
  final VoidCallback onRefresh;
  final ValueChanged<int> onSpotlightPageChanged;

  const _HomeContent({
    required this.homeData,
    required this.onRefresh,
    required this.onSpotlightPageChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final tokens = context.tokens;
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 1024;
    final isCompact = screenWidth < 600;

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(homeProvider);
        await ref.read(homeProvider.future);
      },
      child: CustomScrollView(
        slivers: [
          // --- Spotlight hero ---
          if (homeData.spotlight.isNotEmpty)
            SliverToBoxAdapter(
              child: _SpotlightHero(
                items: homeData.spotlight,
                onPageChanged: onSpotlightPageChanged,
              ),
            ),

          // --- Separator before sections ---
          SliverToBoxAdapter(child: SizedBox(height: tokens.spaceLg)),

          // --- Media type sections with genre rails ---
          for (final section in homeData.mediaTypeSections)
            if (section.genreRails.isNotEmpty)
              SliverToBoxAdapter(
                child: _MediaTypeSection(
                  section: section,
                  isDesktop: isDesktop,
                  isCompact: isCompact,
                ),
              ),

          // Bottom padding
          SliverToBoxAdapter(child: SizedBox(height: tokens.spaceXl)),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Spotlight Hero
// ---------------------------------------------------------------------------
class _SpotlightHero extends StatefulWidget {
  final List<HomeSpotlightItem> items;
  final ValueChanged<int> onPageChanged;

  const _SpotlightHero({
    required this.items,
    required this.onPageChanged,
  });

  @override
  State<_SpotlightHero> createState() => _SpotlightHeroState();
}

class _SpotlightHeroState extends State<_SpotlightHero> {
  late PageController _controller;
  int _currentPage = 0;
  Timer? _cycleTimer;

  @override
  void initState() {
    super.initState();
    _controller = PageController();
    _startCycle();
  }

  @override
  void dispose() {
    _controller.dispose();
    _cycleTimer?.cancel();
    super.dispose();
  }

  void _startCycle() {
    _cycleTimer?.cancel();
    if (widget.items.length <= 1) return;
    _cycleTimer = Timer.periodic(const Duration(seconds: 8), (_) {
      final next = (_currentPage + 1) % widget.items.length;
      _controller.animateToPage(
        next,
        duration: const Duration(milliseconds: 400),
        curve: Curves.easeOutCubic,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 1024;
    final heroHeight = isDesktop ? 460.0 : 360.0;

    return SizedBox(
      height: heroHeight,
      child: Stack(
        children: [
          PageView.builder(
            controller: _controller,
            onPageChanged: (index) {
              setState(() => _currentPage = index);
              widget.onPageChanged(index);
              _startCycle();
            },
            itemCount: widget.items.length,
            itemBuilder: (context, index) {
              final item = widget.items[index];
              return _HeroCard(item: item, heroHeight: heroHeight);
            },
          ),

          // Dot indicators
          if (widget.items.length > 1)
            Positioned(
              bottom: 16,
              left: 0,
              right: 0,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(widget.items.length, (i) {
                  final isActive = i == _currentPage;
                  return AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    width: isActive ? 24 : 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: isActive
                          ? tokens.accentPrimary
                          : tokens.textTertiary.withValues(alpha: 0.4),
                      borderRadius: BorderRadius.circular(4),
                    ),
                  );
                }),
              ),
            ),
        ],
      ),
    );
  }
}

class _HeroCard extends StatelessWidget {
  final HomeSpotlightItem item;
  final double heroHeight;

  const _HeroCard({required this.item, required this.heroHeight});

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 1024;
    final isCompact = screenWidth < 600;

    return Stack(
      fit: StackFit.expand,
      children: [
        // Banner image
        CachedNetworkImage(
          imageUrl: item.bannerImage ?? item.coverImageLarge ?? '',
          fit: BoxFit.cover,
          errorWidget: (_, __, ___) => Container(
            color: tokens.bgSurface,
            child: Center(
              child: Icon(
                Icons.movie_outlined,
                size: 48,
                color: tokens.textTertiary,
              ),
            ),
          ),
        ),

        // Dark gradient scrim
        Positioned.fill(
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter,
                colors: [
                  tokens.bgBase.withValues(alpha: 0.95),
                  tokens.bgBase.withValues(alpha: 0.6),
                  Colors.transparent,
                  Colors.transparent,
                ],
              ),
            ),
          ),
        ),

        // Content overlay
        Positioned(
          bottom: 40,
          left: isCompact ? 16 : (isDesktop ? 72 : 40),
          right: isCompact ? 16 : (isDesktop ? screenWidth * 0.4 : 120),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              // Meta row
              Row(
                children: [
                  if (item.format != null)
                    StatusPill(status: item.format!, fontSize: 11),
                  const SizedBox(width: 8),
                  if (item.averageScore != null)
                    ScoreChip(score: item.averageScore, size: 40, compact: true),
                  if (item.seasonYear != null) ...[
                    const SizedBox(width: 8),
                    Text(
                      '${item.seasonYear}',
                      style: TextStyle(
                        fontFamily: 'Plus Jakarta Sans',
                        fontSize: 13,
                        color: tokens.textSecondary,
                      ),
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 8),

              // Title
              Text(
                item.displayTitle,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontFamily: 'Space Grotesk',
                  fontSize: isDesktop ? 40 : 30,
                  fontWeight: FontWeight.w700,
                  height: isDesktop ? 46 / 40 : 36 / 30,
                  color: tokens.textPrimary,
                ),
              ),
              const SizedBox(height: 8),

              // Synopsis
              if (item.synopsis != null && item.synopsis!.isNotEmpty)
                Text(
                  item.synopsis!,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 15,
                    height: 22 / 15,
                    color: tokens.textSecondary,
                  ),
                ),
              const SizedBox(height: 16),

              // Action buttons
              Row(
                children: [
                  AppButton(
                    label: '+ Add to list',
                    onPressed: () {},
                    variant: AppButtonVariant.primary,
                    height: isCompact ? 40 : 48,
                    fontSize: isCompact ? 14 : 15,
                  ),
                  const SizedBox(width: 12),
                  AppButton(
                    label: 'Details',
                    onPressed: () => context.push('/media/${item.id}'),
                    variant: AppButtonVariant.secondary,
                    height: isCompact ? 40 : 48,
                    fontSize: isCompact ? 14 : 15,
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

// ---------------------------------------------------------------------------
// Media Type Section (Anime / Manga / Manhwa) with genre rails
// ---------------------------------------------------------------------------
class _MediaTypeSection extends StatelessWidget {
  final MediaTypeSection section;
  final bool isDesktop;
  final bool isCompact;

  const _MediaTypeSection({
    required this.section,
    required this.isDesktop,
    required this.isCompact,
  });

  IconData _mediaTypeIcon(String mediaType) {
    switch (mediaType) {
      case 'anime':
        return Icons.videocam_rounded;
      case 'manga':
      case 'manhwa':
        return Icons.menu_book_rounded;
      case 'light_novel':
        return Icons.auto_stories_rounded;
      default:
        return Icons.category_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;

    return Padding(
      padding: EdgeInsets.only(bottom: tokens.spaceLg),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Section heading
          Padding(
            padding: EdgeInsets.symmetric(horizontal: tokens.spaceMd),
            child: Row(
              children: [
                Icon(
                  _mediaTypeIcon(section.mediaType),
                  size: 22,
                  color: tokens.accentPrimary,
                ),
                const SizedBox(width: 8),
                Text(
                  section.mediaTypeLabel,
                  style: TextStyle(
                    fontFamily: 'Space Grotesk',
                    fontSize: 26,
                    fontWeight: FontWeight.w700,
                    color: tokens.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          SizedBox(height: tokens.spaceMd),

          // Genre rails
          for (final genreRail in section.genreRails)
            _GenreRail(
              genreRail: genreRail,
              isDesktop: isDesktop,
              isCompact: isCompact,
            ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Single Genre Rail (horizontal scroll)
// ---------------------------------------------------------------------------
class _GenreRail extends StatelessWidget {
  final GenreRail genreRail;
  final bool isDesktop;
  final bool isCompact;

  const _GenreRail({
    required this.genreRail,
    required this.isDesktop,
    required this.isCompact,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final cardWidth = isDesktop ? 152.0 : 130.0;

    if (genreRail.items.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: EdgeInsets.only(bottom: tokens.spaceSm),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Genre label
          Padding(
            padding: EdgeInsets.only(left: tokens.spaceMd, bottom: 6),
            child: Text(
              genreRail.genreName,
              style: TextStyle(
                fontFamily: 'Plus Jakarta Sans',
                fontSize: 15,
                fontWeight: FontWeight.w600,
                color: tokens.textSecondary,
              ),
            ),
          ),

          // Horizontal scroll of poster cards
          SizedBox(
            height: cardWidth * 1.5 + 10,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              padding: EdgeInsets.only(
                left: tokens.spaceMd,
                right: tokens.spaceLg + 24,
              ),
              itemCount: genreRail.items.length,
              itemExtent: cardWidth + 12,
              itemBuilder: (context, index) {
                final item = genreRail.items[index];
                return Padding(
                  padding: const EdgeInsets.only(right: 12),
                  child: PosterCard(
                    imageUrl: item.coverImageLarge ?? '',
                    title: item.displayTitle,
                    score: item.averageScore,
                    width: cardWidth,
                    onTap: () => context.push('/media/${item.id}'),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// Skeleton loading state
// ---------------------------------------------------------------------------
class _HomeSkeleton extends StatelessWidget {
  const _HomeSkeleton();

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 1024;
    final heroHeight = isDesktop ? 460.0 : 360.0;

    return SingleChildScrollView(
      physics: const NeverScrollableScrollPhysics(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Hero skeleton
          Container(
            height: heroHeight,
            color: tokens.bgSurface,
          ),
          // Section skeleton
          Padding(
            padding: EdgeInsets.only(top: tokens.spaceLg, left: tokens.spaceMd),
            child: Container(
              height: 24,
              width: 120,
              decoration: BoxDecoration(
                color: tokens.bgSurfaceAlt,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
          Padding(
            padding: EdgeInsets.only(top: tokens.spaceMd),
            child: AppSkeleton.rail(),
          ),
          Padding(
            padding: EdgeInsets.only(top: tokens.spaceLg, left: tokens.spaceMd),
            child: Container(
              height: 24,
              width: 100,
              decoration: BoxDecoration(
                color: tokens.bgSurfaceAlt,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
          Padding(
            padding: EdgeInsets.only(top: tokens.spaceMd),
            child: AppSkeleton.rail(),
          ),
        ],
      ),
    );
  }
}
