import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/notifications/models/notification_models.dart';
import 'package:otakuhub/features/notifications/providers/notification_providers.dart';

class NotificationPreferencesScreen extends ConsumerWidget {
  const NotificationPreferencesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncPrefs = ref.watch(notificationPreferencesProviderProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Notification Preferences')),
      body: asyncPrefs.when(
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
                  'Failed to load preferences',
                  style: TextStyle(color: AppColors.textSecondary),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () =>
                      ref.invalidate(notificationPreferencesProviderProvider),
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ),
        data: (prefs) => _PreferencesBody(prefs: prefs),
      ),
    );
  }
}

class _PreferencesBody extends ConsumerStatefulWidget {
  final NotificationPreferences prefs;

  const _PreferencesBody({required this.prefs});

  @override
  ConsumerState<_PreferencesBody> createState() => _PreferencesBodyState();
}

class _PreferencesBodyState extends ConsumerState<_PreferencesBody> {
  late bool _newEpisode;
  late bool _newChapter;
  late bool _friendActivity;
  late bool _recommendations;
  late bool _watchPartyInvite;
  late bool _watchPartyReminder;
  late TextEditingController _discordController;
  late TextEditingController _telegramController;
  late bool _emailEnabled;
  late bool _pushEnabled;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _initFromPrefs(widget.prefs);
  }

  void _initFromPrefs(NotificationPreferences prefs) {
    _newEpisode = prefs.newEpisode;
    _newChapter = prefs.newChapter;
    _friendActivity = prefs.friendActivity;
    _recommendations = prefs.recommendations;
    _watchPartyInvite = prefs.watchPartyInvite;
    _watchPartyReminder = prefs.watchPartyReminder;
    _discordController = TextEditingController(text: prefs.discordWebhook ?? '');
    _telegramController = TextEditingController(text: prefs.telegramChatId ?? '');
    _emailEnabled = prefs.emailEnabled;
    _pushEnabled = prefs.pushEnabled;
  }

  @override
  void didUpdateWidget(_PreferencesBody oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.prefs != widget.prefs) {
      _initFromPrefs(widget.prefs);
    }
  }

  @override
  void dispose() {
    _discordController.dispose();
    _telegramController.dispose();
    super.dispose();
  }

  bool get _hasChanges {
    return _newEpisode != widget.prefs.newEpisode ||
        _newChapter != widget.prefs.newChapter ||
        _friendActivity != widget.prefs.friendActivity ||
        _recommendations != widget.prefs.recommendations ||
        _watchPartyInvite != widget.prefs.watchPartyInvite ||
        _watchPartyReminder != widget.prefs.watchPartyReminder ||
        _discordController.text != (widget.prefs.discordWebhook ?? '') ||
        _telegramController.text != (widget.prefs.telegramChatId ?? '') ||
        _emailEnabled != widget.prefs.emailEnabled ||
        _pushEnabled != widget.prefs.pushEnabled;
  }

  Future<void> _save() async {
    if (!_hasChanges) return;

    setState(() => _saving = true);
    try {
      final updates = NotificationPreferencesUpdate(
        newEpisode: _newEpisode != widget.prefs.newEpisode ? _newEpisode : null,
        newChapter: _newChapter != widget.prefs.newChapter ? _newChapter : null,
        friendActivity: _friendActivity != widget.prefs.friendActivity ? _friendActivity : null,
        recommendations: _recommendations != widget.prefs.recommendations ? _recommendations : null,
        watchPartyInvite: _watchPartyInvite != widget.prefs.watchPartyInvite ? _watchPartyInvite : null,
        watchPartyReminder: _watchPartyReminder != widget.prefs.watchPartyReminder ? _watchPartyReminder : null,
        discordWebhook: _discordController.text.trim().isEmpty
            ? null
            : _discordController.text.trim(),
        telegramChatId: _telegramController.text.trim().isEmpty
            ? null
            : _telegramController.text.trim(),
        emailEnabled: _emailEnabled != widget.prefs.emailEnabled ? _emailEnabled : null,
        pushEnabled: _pushEnabled != widget.prefs.pushEnabled ? _pushEnabled : null,
      );
      await ref.read(updatePreferencesNotifierProvider.notifier).updatePreferences(updates);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Preferences saved')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to save: $e')),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // --- Content section ---
        Text(
          'Content',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          'Choose which types of notifications you receive',
          style: TextStyle(color: AppColors.textMuted, fontSize: 13),
        ),
        const SizedBox(height: 12),

        _buildSwitchTile(
          icon: Icons.play_circle_outline,
          iconColor: AppColors.accentSecondary,
          title: 'New Episodes',
          subtitle: 'When a new episode airs for anime on your list',
          value: _newEpisode,
          onChanged: (v) => setState(() => _newEpisode = v),
        ),
        _buildSwitchTile(
          icon: Icons.auto_stories_outlined,
          iconColor: AppColors.success,
          title: 'New Chapters',
          subtitle: 'When a new chapter is released',
          value: _newChapter,
          onChanged: (v) => setState(() => _newChapter = v),
        ),
        _buildSwitchTile(
          icon: Icons.people_outline,
          iconColor: AppColors.accentPrimary,
          title: 'Friend Activity',
          subtitle: 'When friends update their list or progress',
          value: _friendActivity,
          onChanged: (v) => setState(() => _friendActivity = v),
        ),
        _buildSwitchTile(
          icon: Icons.recommend_outlined,
          iconColor: AppColors.warning,
          title: 'Recommendations',
          subtitle: 'When someone recommends you a title',
          value: _recommendations,
          onChanged: (v) => setState(() => _recommendations = v),
        ),
        _buildSwitchTile(
          icon: Icons.party_mode_outlined,
          iconColor: const Color(0xFFF472B6),
          title: 'Watch Party Invites',
          subtitle: 'When you\'re invited to a watch party',
          value: _watchPartyInvite,
          onChanged: (v) => setState(() => _watchPartyInvite = v),
        ),
        _buildSwitchTile(
          icon: Icons.notifications_active_outlined,
          iconColor: AppColors.destructive,
          title: 'Watch Party Reminders',
          subtitle: 'Reminders before a scheduled watch party',
          value: _watchPartyReminder,
          onChanged: (v) => setState(() => _watchPartyReminder = v),
        ),

        const Divider(height: 32, color: AppColors.borderDefault),

        // --- Channels section ---
        Text(
          'Delivery Channels',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: AppColors.textPrimary,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          'Configure how notifications are delivered',
          style: TextStyle(color: AppColors.textMuted, fontSize: 13),
        ),
        const SizedBox(height: 12),

        // Discord Webhook
        TextFormField(
          controller: _discordController,
          decoration: InputDecoration(
            labelText: 'Discord Webhook URL',
            hintText: 'https://discord.com/api/webhooks/...',
            prefixIcon: const Icon(Icons.discord, size: 20),
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
          maxLines: 1,
        ),
        const SizedBox(height: 14),

        // Telegram Chat ID
        TextFormField(
          controller: _telegramController,
          decoration: InputDecoration(
            labelText: 'Telegram Chat ID',
            hintText: 'e.g. -1001234567890',
            prefixIcon: const Icon(Icons.telegram, size: 20),
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

        _buildSwitchTile(
          icon: Icons.email_outlined,
          iconColor: AppColors.accentSecondary,
          title: 'Email Notifications',
          subtitle: 'Receive email notifications',
          value: _emailEnabled,
          onChanged: (v) => setState(() => _emailEnabled = v),
        ),
        _buildSwitchTile(
          icon: Icons.phone_android_outlined,
          iconColor: AppColors.accentPrimary,
          title: 'Push Notifications',
          subtitle: 'Receive push notifications on your device',
          value: _pushEnabled,
          onChanged: (v) => setState(() => _pushEnabled = v),
        ),

        const SizedBox(height: 24),

        // Save button
        SizedBox(
          width: double.infinity,
          height: 50,
          child: ElevatedButton(
            onPressed: (_saving || !_hasChanges) ? null : _save,
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
            child: _saving
                ? const SizedBox(
                    width: 22,
                    height: 22,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      color: Colors.white,
                    ),
                  )
                : const Text('Save Preferences'),
          ),
        ),
      ],
    );
  }

  Widget _buildSwitchTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: iconColor, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: AppColors.textPrimary,
                  ),
                ),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.textMuted,
                  ),
                ),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeThumbColor: AppColors.accentPrimary,
          ),
        ],
      ),
    );
  }
}
