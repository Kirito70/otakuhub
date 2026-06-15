import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/widgets/app_empty_state.dart';
import '../models/discussion.dart';
import '../providers/discussions_provider.dart';
import '../widgets/reply_card.dart';

class DiscussionDetailScreen extends ConsumerStatefulWidget {
  final String discussionId;

  const DiscussionDetailScreen({super.key, required this.discussionId});

  @override
  ConsumerState<DiscussionDetailScreen> createState() =>
      _DiscussionDetailScreenState();
}

class _DiscussionDetailScreenState
    extends ConsumerState<DiscussionDetailScreen> {
  final _replyController = TextEditingController();
  bool _replyHasSpoilers = false;
  final Set<String> _revealedReplies = {};

  @override
  void dispose() {
    _replyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final repliesAsync = ref.watch(replyListNotifierProvider(widget.discussionId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Discussion'),
      ),
      body: repliesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => AppEmptyState.error(
          message: 'Failed to load discussion',
          onAction: () =>
              ref.invalidate(replyListNotifierProvider(widget.discussionId)),
        ),
        data: (data) => Column(
          children: [
            Expanded(
              child: data.items.isEmpty
                  ? const AppEmptyState(
                      icon: Icons.chat_outlined,
                      message: 'No replies yet. Be the first to reply!',
                    )
                  : ListView.builder(
                      itemCount: data.items.length +
                          (data.items.length < data.total ? 1 : 0),
                      itemBuilder: (context, index) {
                        if (index == data.items.length) {
                          return Padding(
                            padding: const EdgeInsets.all(16),
                            child: Center(
                              child: OutlinedButton(
                                onPressed: () => ref
                                    .read(replyListNotifierProvider(
                                            widget.discussionId)
                                        .notifier)
                                    .loadMore(widget.discussionId),
                                child: const Text('Load More Replies'),
                              ),
                            ),
                          );
                        }
                        final reply = data.items[index];
                        return ReplyCard(
                          reply: reply,
                          isRevealed: _revealedReplies.contains(reply.id),
                          onRevealSpoiler: () {
                            setState(() => _revealedReplies.add(reply.id));
                          },
                        );
                      },
                    ),
            ),
            _buildReplyBar(context),
          ],
        ),
      ),
    );
  }

  Widget _buildReplyBar(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 8,
        bottom: MediaQuery.of(context).padding.bottom + 8,
      ),
      decoration: BoxDecoration(
        color: AppColors.bgSecondary,
        border: Border(
          top: BorderSide(color: AppColors.borderDefault),
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              const Text('Spoiler', style: TextStyle(fontSize: 12)),
              const SizedBox(width: 4),
              Switch(
                value: _replyHasSpoilers,
                onChanged: (v) => setState(() => _replyHasSpoilers = v),
                materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextField(
                  controller: _replyController,
                  decoration: const InputDecoration(
                    hintText: 'Write a reply...',
                    border: OutlineInputBorder(),
                    isDense: true,
                    contentPadding:
                        EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                  ),
                  maxLines: 2,
                  minLines: 1,
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                icon: const Icon(Icons.send),
                color: AppColors.accentPrimary,
                onPressed: _submitReply,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _submitReply() async {
    final body = _replyController.text.trim();
    if (body.isEmpty) return;

    final success = await ref
        .read(createReplyActionProvider.notifier)
        .create(
          widget.discussionId,
          CreateReplyRequest(
            body: body,
            hasSpoilers: _replyHasSpoilers,
          ),
        );

    if (success && mounted) {
      _replyController.clear();
      setState(() => _replyHasSpoilers = false);
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to post reply')),
      );
    }
  }
}
