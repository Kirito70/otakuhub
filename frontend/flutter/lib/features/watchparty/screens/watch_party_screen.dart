import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/watchparty/models/watch_party.dart';
import 'package:otakuhub/features/watchparty/providers/watch_party_provider.dart';
import 'package:otakuhub/features/watchparty/widgets/date_utils.dart';
import 'package:otakuhub/features/watchparty/widgets/party_card.dart';
import 'package:otakuhub/features/watchparty/widgets/party_detail_sheet.dart';

class WatchPartyScreen extends ConsumerStatefulWidget {
  final int initialTabIndex;

  const WatchPartyScreen({super.key, this.initialTabIndex = 0});

  @override
  ConsumerState<WatchPartyScreen> createState() => _WatchPartyScreenState();
}

class _WatchPartyScreenState extends ConsumerState<WatchPartyScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  bool _pastTabVisited = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(
      length: 3,
      vsync: this,
      initialIndex: widget.initialTabIndex,
    );
    _tabController.addListener(_onTabChanged);
  }

  void _onTabChanged() {
    if (_tabController.index == 1 && !_pastTabVisited) {
      _pastTabVisited = true;
      // Past tab lazily loads via its own provider — no explicit trigger needed
    }
  }

  @override
  void dispose() {
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    super.dispose();
  }

  void _openDetailSheet(String partyId) {
    showModalBottomSheet<dynamic>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => PartyDetailSheet(partyId: partyId),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Watch Party'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Upcoming'),
            Tab(text: 'Past'),
            Tab(text: 'Create'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _UpcomingTab(onTapParty: _openDetailSheet),
          _PastTab(onTapParty: _openDetailSheet),
          _CreateTab(
            onSuccess: () => _tabController.animateTo(0),
          ),
        ],
      ),
    );
  }
}

// --- Upcoming Tab ---

class _UpcomingTab extends ConsumerWidget {
  final void Function(String partyId) onTapParty;

  const _UpcomingTab({required this.onTapParty});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncParties = ref.watch(upcomingPartiesNotifierProvider);

    return asyncParties.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline,
                  color: AppColors.destructive, size: 48),
              const SizedBox(height: 12),
              Text(
                'Failed to load upcoming parties',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () =>
                    ref.invalidate(upcomingPartiesNotifierProvider),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.event_busy_outlined,
                    size: 64, color: AppColors.textMuted),
                const SizedBox(height: 16),
                Text(
                  'No upcoming parties',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Create one to get started!',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              ],
            ),
          );
        }
        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(upcomingPartiesNotifierProvider);
          },
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(vertical: 8),
            itemCount: data.items.length,
            itemBuilder: (context, index) {
              final party = data.items[index];
              final notifier = ref.read(
                upcomingPartiesNotifierProvider.notifier,
              );
              return PartyCard(
                party: party,
                showAttendButton: true,
                onTap: () => onTapParty(party.id),
                onAttend: () {
                  notifier; // for loadMore if needed
                  ref.read(rsvpNotifierProvider.notifier).rsvp(
                        partyId: party.id,
                        status: 'attending',
                      );
                },
              );
            },
          ),
        );
      },
    );
  }
}

// --- Past Tab ---

class _PastTab extends ConsumerWidget {
  final void Function(String partyId) onTapParty;

  const _PastTab({required this.onTapParty});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncParties = ref.watch(pastPartiesNotifierProvider);

    return asyncParties.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (err, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline,
                  color: AppColors.destructive, size: 48),
              const SizedBox(height: 12),
              Text(
                'Failed to load past parties',
                style: TextStyle(color: AppColors.textSecondary),
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.invalidate(pastPartiesNotifierProvider),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
      data: (data) {
        if (data.items.isEmpty) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.history,
                    size: 64, color: AppColors.textMuted),
                const SizedBox(height: 16),
                Text(
                  'No past parties',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: AppColors.textSecondary,
                      ),
                ),
              ],
            ),
          );
        }
        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(pastPartiesNotifierProvider);
          },
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(vertical: 8),
            itemCount: data.items.length,
            itemBuilder: (context, index) {
              final party = data.items[index];
              return PartyCard(
                party: party,
                onTap: () => onTapParty(party.id),
              );
            },
          ),
        );
      },
    );
  }
}

// --- Create Tab ---

class _CreateTab extends ConsumerStatefulWidget {
  final VoidCallback onSuccess;

  const _CreateTab({required this.onSuccess});

  @override
  ConsumerState<_CreateTab> createState() => _CreateTabState();
}

class _CreateTabState extends ConsumerState<_CreateTab> {
  final _formKey = GlobalKey<FormState>();
  final _groupIdController = TextEditingController();
  final _mediaIdController = TextEditingController();
  final _titleController = TextEditingController();
  final _episodeController = TextEditingController();
  final _streamUrlController = TextEditingController();
  final _notesController = TextEditingController();
  DateTime? _selectedDate;

  @override
  void dispose() {
    _groupIdController.dispose();
    _mediaIdController.dispose();
    _titleController.dispose();
    _episodeController.dispose();
    _streamUrlController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _pickDate() async {
    final now = DateTime.now();
    final date = await showDatePicker(
      context: context,
      initialDate: _selectedDate ?? now.add(const Duration(hours: 1)),
      firstDate: now,
      lastDate: now.add(const Duration(days: 365)),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: Theme.of(context).colorScheme.copyWith(
                  primary: AppColors.accentPrimary,
                ),
          ),
          child: child!,
        );
      },
    );
    if (date != null) {
      if (!mounted) return;
      final time = await showTimePicker(
        context: context,
        initialTime: TimeOfDay.fromDateTime(
          _selectedDate ?? DateTime.now(),
        ),
      );
      if (time != null) {
        setState(() {
          _selectedDate = DateTime(
            date.year,
            date.month,
            date.day,
            time.hour,
            time.minute,
          );
        });
      }
    }
  }

  Future<void> _handleSubmit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedDate == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a date and time')),
      );
      return;
    }

    try {
      final request = WatchPartyCreateRequest(
        groupId: _groupIdController.text.trim(),
        mediaId: _mediaIdController.text.trim(),
        scheduledAt: _selectedDate!,
        title: _titleController.text.trim().isEmpty
            ? null
            : _titleController.text.trim(),
        episodeNumber: _episodeController.text.trim().isEmpty
            ? null
            : int.tryParse(_episodeController.text.trim()),
        streamUrl: _streamUrlController.text.trim().isEmpty
            ? null
            : _streamUrlController.text.trim(),
        notes: _notesController.text.trim().isEmpty
            ? null
            : _notesController.text.trim(),
      );

      await ref.read(createPartyNotifierProvider.notifier).create(request);

      if (!mounted) return;

      // Clear form
      _groupIdController.clear();
      _mediaIdController.clear();
      _titleController.clear();
      _episodeController.clear();
      _streamUrlController.clear();
      _notesController.clear();
      setState(() => _selectedDate = null);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Watch party created!')),
      );

      widget.onSuccess();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to create: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final createAsync = ref.watch(createPartyNotifierProvider);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'New Watch Party',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
            ),
            const SizedBox(height: 24),

            // Group ID
            TextFormField(
              controller: _groupIdController,
              decoration: InputDecoration(
                labelText: 'Group ID *',
                hintText: 'Enter the group UUID',
                prefixIcon:
                    const Icon(Icons.group_outlined, size: 20),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.06),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: Colors.white.withValues(alpha: 0.1),
                  ),
                ),
              ),
              style: const TextStyle(color: Colors.white),
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'Group ID is required' : null,
            ),
            const SizedBox(height: 14),

            // Media ID
            TextFormField(
              controller: _mediaIdController,
              decoration: InputDecoration(
                labelText: 'Media ID *',
                hintText: 'Media UUID to watch',
                prefixIcon:
                    const Icon(Icons.movie_outlined, size: 20),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.06),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: Colors.white.withValues(alpha: 0.1),
                  ),
                ),
              ),
              style: const TextStyle(color: Colors.white),
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'Media ID is required' : null,
            ),
            const SizedBox(height: 14),

            // Title (optional)
            TextFormField(
              controller: _titleController,
              decoration: InputDecoration(
                labelText: 'Title (optional)',
                hintText: 'E.g. Solo Leveling Watch Party',
                prefixIcon:
                    const Icon(Icons.label_outline, size: 20),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.06),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: Colors.white.withValues(alpha: 0.1),
                  ),
                ),
              ),
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 14),

            // Episode number (optional)
            TextFormField(
              controller: _episodeController,
              decoration: InputDecoration(
                labelText: 'Episode (optional)',
                hintText: 'E.g. 12',
                prefixIcon:
                    const Icon(Icons.play_circle_outline, size: 20),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.06),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: Colors.white.withValues(alpha: 0.1),
                  ),
                ),
              ),
              style: const TextStyle(color: Colors.white),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 14),

            // Date/time picker
            InkWell(
              onTap: _pickDate,
              borderRadius: BorderRadius.circular(12),
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 16),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.06),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: Colors.white.withValues(alpha: 0.1),
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.schedule_outlined,
                        size: 20, color: AppColors.textSecondary),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Date & Time *',
                          style: TextStyle(
                            fontSize: 12,
                            color: AppColors.textMuted,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          _selectedDate != null
                              ? formatDateFull(_selectedDate!)
                              : 'Tap to select',
                          style: TextStyle(
                            fontSize: 14,
                            color: _selectedDate != null
                                ? AppColors.textPrimary
                                : AppColors.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 14),

            // Stream URL (optional)
            TextFormField(
              controller: _streamUrlController,
              decoration: InputDecoration(
                labelText: 'Stream URL (optional)',
                hintText: 'URL to the streaming session',
                prefixIcon:
                    const Icon(Icons.link_outlined, size: 20),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.06),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: Colors.white.withValues(alpha: 0.1),
                  ),
                ),
              ),
              style: const TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 14),

            // Notes (optional)
            TextFormField(
              controller: _notesController,
              decoration: InputDecoration(
                labelText: 'Notes (optional)',
                hintText: 'Any additional info',
                prefixIcon:
                    const Icon(Icons.notes_outlined, size: 20),
                filled: true,
                fillColor: Colors.white.withValues(alpha: 0.06),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: Colors.white.withValues(alpha: 0.1),
                  ),
                ),
              ),
              style: const TextStyle(color: Colors.white),
              maxLines: 3,
            ),
            const SizedBox(height: 24),

            // Submit button
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed:
                    createAsync.isLoading ? null : _handleSubmit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.accentPrimary,
                  foregroundColor: Colors.white,
                  disabledBackgroundColor:
                      AppColors.accentPrimary.withValues(alpha: 0.3),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  textStyle: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                child: createAsync.isLoading
                    ? const SizedBox(
                        width: 22,
                        height: 22,
                        child: CircularProgressIndicator(
                          strokeWidth: 2.5,
                          color: Colors.white,
                        ),
                      )
                    : const Text('Create Party'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
