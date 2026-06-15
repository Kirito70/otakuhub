import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class CreateWatchPartyScreen extends ConsumerWidget {
  const CreateWatchPartyScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(title: const Text('Create Party')),
      body: const Center(child: Text('Create Watch Party — wireframe')),
    );
  }
}
