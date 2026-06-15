import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/media_detail/models/media_detail.dart';
import 'package:otakuhub/features/media_detail/providers/media_detail_providers.dart';
import 'package:otakuhub/features/media_detail/widgets/episodes_tab.dart';
import 'package:otakuhub/features/media_detail/widgets/hero_banner.dart';
import 'package:otakuhub/features/media_detail/widgets/info_tab.dart';
import 'package:otakuhub/features/media_detail/widgets/related_carousel.dart';

class MediaDetailScreen extends ConsumerStatefulWidget {
  final String mediaId;

  const MediaDetailScreen({super.key, required this.mediaId});

  @override
  ConsumerState<MediaDetailScreen> createState() => _MediaDetailScreenState();
}

class _MediaDetailScreenState extends ConsumerState<MediaDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final mediaAsync = ref.watch(mediaDetailProvider(widget.mediaId));

    return mediaAsync.when(
      loading: () => const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      ),
      error: (err, _) => Scaffold(
        appBar: AppBar(),
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 48, color: AppColors.destructive),
              const SizedBox(height: 12),
              const Text('Failed to load media details',
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 16)),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => ref.invalidate(mediaDetailProvider(widget.mediaId)),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
      data: (media) {
        if (media == null) {
          return Scaffold(
            appBar: AppBar(),
            body: const Center(
              child: Text('Media not found',
                  style: TextStyle(color: AppColors.textSecondary)),
            ),
          );
        }
        return _buildContent(media);
      },
    );
  }

  Widget _buildContent(MediaDetail media) {
    return Scaffold(
      body: NestedScrollView(
        headerSliverBuilder: (context, innerBoxIsScrolled) {
          return [
            SliverToBoxAdapter(
              child: HeroBanner(
                title: media.displayTitle,
                bannerImage: media.bannerImage,
                coverImage: media.coverImageLarge ?? media.coverImageMedium,
                score: media.averageScore,
                year: media.seasonYear?.toString(),
                mediaType: media.mediaType,
                format: media.format,
                status: media.status,
                episodeCount: media.episodeCount,
                genres: media.genres?.map((g) => g.name).toList(),
                onPlay: media.mediaType == 'anime' && media.episodeCount != null
                    ? () {
                        // TODO: Navigate to video player
                      }
                    : null,
                onAddToList: () {
                  // TODO: Open add-to-list dialog
                },
              ),
            ),
            SliverPersistentHeader(
              pinned: true,
              delegate: _TabBarDelegate(
                tabController: _tabController,
                episodeCount: media.episodeCount,
              ),
            ),
          ];
        },
        body: TabBarView(
          controller: _tabController,
          children: [
            // Episodes tab (or chapters for manga/manhwa)
            _buildEpisodesOrChaptersTab(media),
            // Info tab
            InfoTab(media: media),
            // Related tab
            _buildRelationsTab(media),
          ],
        ),
      ),
    );
  }

  Widget _buildEpisodesOrChaptersTab(MediaDetail media) {
    if (media.mediaType == 'anime') {
      return _buildEpisodesTab();
    } else {
      return _buildChaptersPlaceholder();
    }
  }

  Widget _buildEpisodesTab() {
    final episodesAsync = ref.watch(episodesProvider(widget.mediaId));
    return episodesAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (_, __) => const Center(
        child: Text('Failed to load episodes',
            style: TextStyle(color: AppColors.textSecondary)),
      ),
      data: (episodes) => EpisodesTab(episodes: episodes),
    );
  }

  Widget _buildChaptersPlaceholder() {
    return const Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.menu_book_outlined, size: 48, color: AppColors.textMuted),
          SizedBox(height: 8),
          Text('Chapter data not yet available',
              style: TextStyle(color: AppColors.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildRelationsTab(MediaDetail media) {
    final relationsAsync = ref.watch(mediaRelationsProvider(widget.mediaId));
    return relationsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (_, __) => const Center(
        child: Text('Failed to load related media',
            style: TextStyle(color: AppColors.textSecondary)),
      ),
      data: (relations) => RelatedCarousel(relations: relations),
    );
  }
}

// -- Persistent header delegate for sticky tab bar --
class _TabBarDelegate extends SliverPersistentHeaderDelegate {
  final TabController tabController;
  final int? episodeCount;

  _TabBarDelegate({required this.tabController, this.episodeCount});

  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    final isScrolled = shrinkOffset > 20;
    return Container(
      color: isScrolled ? AppColors.bgPrimary : AppColors.bgPrimary.withValues(alpha: 0.8),
      child: TabBar(
        controller: tabController,
        indicatorColor: AppColors.accentPrimary,
        labelColor: AppColors.accentPrimary,
        unselectedLabelColor: AppColors.textSecondary,
        tabs: [
          const Tab(text: 'Episodes'),
          const Tab(text: 'Info'),
          const Tab(text: 'Related'),
        ],
      ),
    );
  }

  @override
  double get maxExtent => 48;

  @override
  double get minExtent => 48;

  @override
  bool shouldRebuild(covariant _TabBarDelegate oldDelegate) => false;
}
