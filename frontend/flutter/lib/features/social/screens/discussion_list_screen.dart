import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_empty_state.dart';
import '../models/discussion.dart';
import '../providers/discussions_provider.dart';
import '../widgets/discussion_card.dart';

class DiscussionListScreen extends ConsumerStatefulWidget {
  const DiscussionListScreen({super.key});

  @override
  ConsumerState<DiscussionListScreen> createState() =>
      _DiscussionListScreenState();
}

class _DiscussionListScreenState extends ConsumerState<DiscussionListScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  final _mediaIdController = TextEditingController();
  final _titleController = TextEditingController();
  final _bodyController = TextEditingController();
  final _episodeController = TextEditingController();
  final _spoilerToggle = ValueNotifier<bool>(false);
  String? _searchedMediaId;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _mediaIdController.dispose();
    _titleController.dispose();
    _bodyController.dispose();
    _episodeController.dispose();
    _spoilerToggle.dispose();
    super.dispose();
  }

  void _fetchDiscussions() {
    final id = _mediaIdController.text.trim();
    if (id.isEmpty) return;
    setState(() => _searchedMediaId = id);
    ref.invalidate(discussionListNotifierProvider(id));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Discussions'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Threads'),
            Tab(text: 'Create'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _ThreadsTab(
            mediaIdController: _mediaIdController,
            searchedMediaId: _searchedMediaId,
            onSearch: _fetchDiscussions,
          ),
          _CreateTab(
            titleController: _titleController,
            bodyController: _bodyController,
            episodeController: _episodeController,
            spoilerToggle: _spoilerToggle,
            mediaIdController: _mediaIdController,
            tabController: _tabController,
            onCreated: _fetchDiscussions,
          ),
        ],
      ),
    );
  }
}

class _ThreadsTab extends ConsumerWidget {
  final TextEditingController mediaIdController;
  final String? searchedMediaId;
  final VoidCallback onSearch;

  const _ThreadsTab({
    required this.mediaIdController,
    required this.searchedMediaId,
    required this.onSearch,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (searchedMediaId == null || searchedMediaId!.isEmpty) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: mediaIdController,
              decoration: const InputDecoration(
                labelText: 'Media ID',
                hintText: 'Enter a Media UUID to view discussions',
                border: OutlineInputBorder(),
                suffixIcon: Icon(Icons.search),
              ),
              onSubmitted: (_) => onSearch(),
            ),
            const SizedBox(height: 16),
            const Expanded(
              child: Center(
                child: Text(
                  'Enter a Media ID above to view discussions.',
                  style: TextStyle(color: AppColors.textMuted),
                  textAlign: TextAlign.center,
                ),
              ),
            ),
          ],
        ),
      );
    }

    final discussionsAsync =
        ref.watch(discussionListNotifierProvider(searchedMediaId!));

    return discussionsAsync.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => AppEmptyState.error(
        message: 'Failed to load discussions',
        onAction: () => onSearch(),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return const AppEmptyState(
            icon: Icons.forum_outlined,
            message: 'No discussions for this media yet.',
          );
        }
        return ListView.separated(
          itemCount:
              data.items.length + (data.items.length < data.total ? 1 : 0),
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, index) {
            if (index == data.items.length) {
              return Padding(
                padding: const EdgeInsets.all(16),
                child: Center(
                  child: OutlinedButton(
                    onPressed: () => ref
                        .read(
                            discussionListNotifierProvider(searchedMediaId!)
                                .notifier)
                        .loadMore(searchedMediaId!),
                    child: const Text('Load More'),
                  ),
                ),
              );
            }
            final disc = data.items[index];
            return DiscussionCard(
              discussion: disc,
              onTap: () => context.push('/discussions/${disc.id}'),
            );
          },
        );
      },
    );
  }
}

class _CreateTab extends ConsumerWidget {
  final TextEditingController titleController;
  final TextEditingController bodyController;
  final TextEditingController episodeController;
  final ValueNotifier<bool> spoilerToggle;
  final TextEditingController mediaIdController;
  final TabController tabController;
  final VoidCallback onCreated;

  const _CreateTab({
    required this.titleController,
    required this.bodyController,
    required this.episodeController,
    required this.spoilerToggle,
    required this.mediaIdController,
    required this.tabController,
    required this.onCreated,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final groupId = '';
    // For simplicity, we use an empty group_id — backend will validate.
    // In a later phase, group selection UI can be added.

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          TextField(
            controller: mediaIdController,
            decoration: const InputDecoration(
              labelText: 'Media ID *',
              hintText: 'UUID of the media entry',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: titleController,
            decoration: const InputDecoration(
              labelText: 'Title (optional)',
              hintText: 'Discussion title',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: bodyController,
            maxLines: 4,
            decoration: const InputDecoration(
              labelText: 'Body *',
              hintText: 'Write your discussion content...',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              ValueListenableBuilder<bool>(
                valueListenable: spoilerToggle,
                builder: (context, value, _) {
                  return Row(
                    children: [
                      const Text('Contains spoilers'),
                      const SizedBox(width: 8),
                      Switch(
                        value: value,
                        onChanged: (v) => spoilerToggle.value = v,
                      ),
                    ],
                  );
                },
              ),
              const SizedBox(width: 16),
              SizedBox(
                width: 120,
                child: TextField(
                  controller: episodeController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Episode (opt)',
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          FilledButton.icon(
            onPressed: () async {
              final mediaId = mediaIdController.text.trim();
              final body = bodyController.text.trim();
              if (mediaId.isEmpty || body.isEmpty) return;

              final request = CreateDiscussionRequest(
                mediaId: mediaId,
                groupId: groupId,
                title: titleController.text.trim().isEmpty
                    ? null
                    : titleController.text.trim(),
                body: body,
                hasSpoilers: spoilerToggle.value,
                episodeNumber: episodeController.text.trim().isEmpty
                    ? null
                    : int.tryParse(episodeController.text.trim()),
              );

              final discussion = await ref
                  .read(createDiscussionActionProvider.notifier)
                  .create(request);

              if (discussion != null && context.mounted) {
                titleController.clear();
                bodyController.clear();
                episodeController.clear();
                spoilerToggle.value = false;
                onCreated();
                tabController.animateTo(0);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Discussion created!')),
                );
              } else if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Failed to create discussion'),
                  ),
                );
              }
            },
            icon: const Icon(Icons.add_comment),
            label: const Text('Create Discussion'),
          ),
        ],
      ),
    );
  }
}
