import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class WatchPartyListScreen extends ConsumerWidget {
  const WatchPartyListScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Watch Party')),
      body: const Center(child: Text('Watch Party — wireframe')),
    );
  }
}
