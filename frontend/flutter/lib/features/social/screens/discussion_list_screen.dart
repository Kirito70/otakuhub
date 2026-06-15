import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DiscussionListScreen extends ConsumerWidget {
  const DiscussionListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Discussions')),
      body: const Center(child: Text('Discussions — wireframe')),
    );
  }
}
