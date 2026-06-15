import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DiscussionDetailScreen extends ConsumerWidget {
  final String discussionId;

  const DiscussionDetailScreen({super.key, required this.discussionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Discussion')),
      body: Center(child: Text('Discussion Detail — wireframe (id: $discussionId)')),
    );
  }
}
