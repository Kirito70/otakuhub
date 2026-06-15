import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/tracking/models/import_models.dart';
import 'package:otakuhub/features/tracking/providers/sync_providers.dart';

class ImportListScreen extends ConsumerStatefulWidget {
  const ImportListScreen({super.key});

  @override
  ConsumerState<ImportListScreen> createState() => _ImportListScreenState();
}

class _ImportListScreenState extends ConsumerState<ImportListScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _usernameController = TextEditingController();
  bool _overwriteExisting = false;
  bool _isImporting = false;
  String? _error;
  String? _activeJobId;
  String? _activeProvider;

  // Per-tab form keys to avoid DuplicateGlobalKey in TabBarView
  final _formKeyAnilist = GlobalKey<FormState>();
  final _formKeyMal = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _tabController.addListener(_onTabChanged);
  }

  @override
  void dispose() {
    _tabController.removeListener(_onTabChanged);
    _tabController.dispose();
    _usernameController.dispose();
    super.dispose();
  }

  void _onTabChanged() {
    if (!_tabController.indexIsChanging) {
      setState(() {
        _error = null;
      });
    }
  }

  String get _currentProvider => _tabController.index == 0 ? 'anilist' : 'mal';

  String get _providerLabel => _currentProvider == 'anilist' ? 'AniList' : 'MyAnimeList';

  List<String>? _validateUsername(String? value) {
    if (value == null || value.trim().isEmpty) {
      return null; // username is optional
    }
    final trimmed = value.trim();

    if (_currentProvider == 'anilist') {
      final validChars = RegExp(r'^[a-zA-Z0-9_-]+$');
      if (!validChars.hasMatch(trimmed)) {
        return ['AniList usernames: letters, numbers, dashes, and underscores only.'];
      }
      if (trimmed.length < 3 || trimmed.length > 20) {
        return ['AniList usernames: 3–20 characters.'];
      }
    } else {
      final validChars = RegExp(r'^[a-zA-Z0-9_]+$');
      if (!validChars.hasMatch(trimmed)) {
        return ['MAL usernames: letters, numbers, and underscores only.'];
      }
      if (trimmed.length < 3 || trimmed.length > 16) {
        return ['MAL usernames: 3–16 characters.'];
      }
    }
    return null;
  }

  GlobalKey<FormState> get _currentFormKey =>
      _currentProvider == 'anilist' ? _formKeyAnilist : _formKeyMal;

  Future<void> _onImport() async {
    if (!_currentFormKey.currentState!.validate()) return;

    setState(() {
      _isImporting = true;
      _error = null;
      _activeJobId = null;
      _activeProvider = null;
    });

    final params = SyncImportParams(
      provider: _currentProvider,
      username: _usernameController.text.trim().isEmpty
          ? null
          : _usernameController.text.trim(),
      overwriteExisting: _overwriteExisting,
    );

    try {
      final result = await ref.read(syncImportProvider(params).future);
      setState(() {
        _isImporting = false;
        _activeJobId = result.jobId;
        _activeProvider = _currentProvider;
      });
    } catch (e) {
      setState(() {
        _isImporting = false;
        if (e is DioException) {
          if (e.response?.statusCode == 429) {
            _error = 'Rate limited. Please wait a moment and try again.';
          } else {
            _error = 'Import failed: ${e.response?.data?['detail'] ?? e.message}';
          }
        } else {
          _error = 'Import failed: $e';
        }
      });
    }
  }

  void _resetImport() {
    setState(() {
      _activeJobId = null;
      _activeProvider = null;
      _error = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Import List'),
      ),
      body: Column(
        children: [
          TabBar(
            controller: _tabController,
            tabs: const [
              Tab(text: 'AniList'),
              Tab(text: 'MyAnimeList'),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildImportForm(context, provider: 'anilist'),
                _buildImportForm(context, provider: 'mal'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImportForm(BuildContext context, {required String provider}) {
    if (_activeJobId != null) {
      return _buildJobStatus(context);
    }

    final formKey = provider == 'anilist' ? _formKeyAnilist : _formKeyMal;
    return Form(
      key: formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Info banner
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppColors.accentPrimary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline, color: AppColors.accentPrimary, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _currentProvider == 'anilist'
                        ? 'AniList usernames: 3–20 characters, letters, numbers, dashes, and underscores.'
                        : 'MyAnimeList usernames: 3–16 characters, letters, numbers, and underscores.',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppColors.accentPrimary,
                        ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Username field
          TextFormField(
            controller: _usernameController,
            decoration: InputDecoration(
              labelText: 'Username (optional)',
              hintText: 'Enter $_providerLabel username',
              border: const OutlineInputBorder(),
              prefixIcon: const Icon(Icons.person),
            ),
            validator: (value) {
              final errors = _validateUsername(value);
              if (errors != null && errors.isNotEmpty) {
                return errors.first;
              }
              return null;
            },
            onChanged: (_) {
              // Clear error on input
              if (_error != null) {
                setState(() => _error = null);
              }
            },
          ),
          const SizedBox(height: 16),

          // Overwrite toggle
          CheckboxListTile(
            value: _overwriteExisting,
            onChanged: (v) => setState(() => _overwriteExisting = v ?? false),
            title: const Text('Overwrite existing entries'),
            subtitle: const Text(
              'Update progress and scores for titles already in your list.',
            ),
            controlAffinity: ListTileControlAffinity.leading,
            contentPadding: EdgeInsets.zero,
          ),

          // Error banner
          if (_error != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.destructive.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error, color: AppColors.destructive, size: 20),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      _error!,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppColors.destructive,
                          ),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 24),

          // Submit button
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _isImporting ? null : _onImport,
              icon: _isImporting
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.cloud_download),
              label: Text(_isImporting ? 'Starting...' : 'Start Import'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildJobStatus(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Job status card
        Card(
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: ref.watch(syncJobStatusStreamProvider(_activeJobId!)).when(
                  loading: () => _buildRunningStatus(context),
                  error: (err, _) => _buildRunningStatus(context),
                  data: (status) {
                    if (status == null) {
                      return _buildRunningStatus(context);
                    }
                    return _buildStatusContent(context, status);
                  },
                ),
          ),
        ),
      ],
    );
  }

  Widget _buildRunningStatus(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const SizedBox(
          width: 40,
          height: 40,
          child: CircularProgressIndicator(strokeWidth: 3),
        ),
        const SizedBox(height: 16),
        Text(
          'Import in progress...',
          style: Theme.of(context).textTheme.titleMedium,
        ),
        const SizedBox(height: 8),
        Text(
          'Fetching your $_activeProvider list.',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppColors.textSecondary,
              ),
        ),
        const SizedBox(height: 16),
        Text(
          'Job ID: ${_activeJobId!.substring(0, 8)}...',
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: AppColors.textMuted,
              ),
        ),
      ],
    );
  }

  Widget _buildStatusContent(BuildContext context, SyncJobStatusResponse status) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Icon based on status
        if (status.isRunning) ...[
          const SizedBox(
            width: 40,
            height: 40,
            child: CircularProgressIndicator(strokeWidth: 3),
          ),
          const SizedBox(height: 16),
          Text(
            'Import in progress...',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          if (status.totalItems != null && status.totalItems! > 0)
            LinearProgressIndicator(
              value: status.processedItems / status.totalItems!,
            ),
          const SizedBox(height: 8),
          Text(
            '${status.processedItems} item${status.processedItems != 1 ? 's' : ''} processed${status.totalItems != null ? ' of ${status.totalItems}' : ''}',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
        ] else if (status.isCompleted) ...[
          const Icon(Icons.check_circle, color: AppColors.success, size: 48),
          const SizedBox(height: 16),
          Text(
            'Import completed',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppColors.success,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            '${status.processedItems} item${status.processedItems != 1 ? 's' : ''} imported.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
        ] else if (status.isPartial) ...[
          const Icon(Icons.warning, color: AppColors.warning, size: 48),
          const SizedBox(height: 16),
          Text(
            'Import completed with errors',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppColors.warning,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            '${status.processedItems} item${status.processedItems != 1 ? 's' : ''} imported, ${status.failedItems} failed.',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.textSecondary,
                ),
          ),
        ] else ...[
          // Failed
          const Icon(Icons.error, color: AppColors.destructive, size: 48),
          const SizedBox(height: 16),
          Text(
            'Import failed',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: AppColors.destructive,
                ),
          ),
          if (status.errorLog != null && status.errorLog!.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              status.errorLog!,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.destructive,
                  ),
              textAlign: TextAlign.center,
            ),
          ],
        ],

        const SizedBox(height: 16),
        Text(
          'Job ID: ${status.id.substring(0, 8)}...',
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: AppColors.textMuted,
              ),
        ),

        if (!status.isRunning) ...[
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: _resetImport,
              icon: const Icon(Icons.refresh),
              label: const Text('Start New Import'),
            ),
          ),
        ],
      ],
    );
  }
}
