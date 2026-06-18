import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/features/profile/models/user_profile.dart';
import 'package:otakuhub/features/profile/providers/profile_provider.dart';

/// Common timezones for the dropdown selector.
const List<String> commonTimezones = [
  'UTC',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'Europe/London',
  'Europe/Berlin',
  'Europe/Paris',
  'Asia/Tokyo',
  'Asia/Seoul',
  'Asia/Shanghai',
  'Asia/Kolkata',
  'Australia/Sydney',
  'Pacific/Auckland',
];

class EditProfileScreen extends ConsumerStatefulWidget {
  const EditProfileScreen({super.key});

  @override
  ConsumerState<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends ConsumerState<EditProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _displayNameController = TextEditingController();
  final _avatarUrlController = TextEditingController();
  final _bioController = TextEditingController();
  String _selectedTimezone = 'UTC';
  bool _isSaving = false;
  String? _errorMessage;
  String? _successMessage;

  @override
  void dispose() {
    _displayNameController.dispose();
    _avatarUrlController.dispose();
    _bioController.dispose();
    super.dispose();
  }

  /// Hydrate form fields from the loaded profile.
  void _hydrateFromProfile(UserProfile profile) {
    _displayNameController.text = profile.displayName ?? '';
    _avatarUrlController.text = profile.avatarUrl ?? '';
    _bioController.text = profile.bio ?? '';
    _selectedTimezone = profile.timezone;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isSaving = true;
      _errorMessage = null;
      _successMessage = null;
    });

    final update = UserUpdate(
      displayName: _displayNameController.text.trim().isEmpty
          ? null
          : _displayNameController.text.trim(),
      avatarUrl: _avatarUrlController.text.trim().isEmpty
          ? null
          : _avatarUrlController.text.trim(),
      bio: _bioController.text.trim().isEmpty
          ? null
          : _bioController.text.trim(),
      timezone: _selectedTimezone,
    );

    final notifier = ref.read(profileUpdateProvider.notifier);
    final result = await notifier.updateProfile(update);

    if (!mounted) return;

    setState(() => _isSaving = false);

    if (result != null) {
      setState(() => _successMessage = 'Profile updated successfully.');
    } else {
      setState(() {
        _errorMessage = 'Failed to update profile. Please try again.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final profileAsync = ref.watch(profileProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Edit Profile')),
      body: profileAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.error_outline,
                  size: 48, color: AppColors.destructive),
              const SizedBox(height: 16),
              Text('Failed to load profile',
                  style: theme.textTheme.titleMedium),
              const SizedBox(height: 24),
              FilledButton.icon(
                onPressed: () => ref.invalidate(profileProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('Retry'),
              ),
            ],
          ),
        ),
        data: (profile) {
          // Hydrate form on first load
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (_displayNameController.text.isEmpty &&
                _avatarUrlController.text.isEmpty &&
                _bioController.text.isEmpty) {
              _hydrateFromProfile(profile);
            }
          });

          return Form(
            key: _formKey,
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // --- Success banner ---
                if (_successMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.success.withAlpha(25),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                          color: AppColors.success.withAlpha(80)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.check_circle,
                            color: AppColors.success, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _successMessage!,
                            style: TextStyle(color: AppColors.success),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // --- Error banner ---
                if (_errorMessage != null) ...[
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.destructive.withAlpha(25),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                          color: AppColors.destructive.withAlpha(80)),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.error,
                            color: AppColors.destructive, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            _errorMessage!,
                            style: TextStyle(color: AppColors.destructive),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                ],

                // --- Display Name ---
                TextFormField(
                  controller: _displayNameController,
                  decoration: const InputDecoration(
                    labelText: 'Display Name',
                    hintText: 'How others see you',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                  maxLength: 100,
                  textInputAction: TextInputAction.next,
                ),
                const SizedBox(height: 16),

                // --- Avatar URL ---
                TextFormField(
                  controller: _avatarUrlController,
                  decoration: const InputDecoration(
                    labelText: 'Avatar URL',
                    hintText: 'https://example.com/avatar.png',
                    prefixIcon: Icon(Icons.link),
                  ),
                  maxLength: 2048,
                  textInputAction: TextInputAction.next,
                  validator: (value) {
                    if (value != null && value.isNotEmpty) {
                      if (!Uri.tryParse(value)!.isAbsolute) {
                        return 'Please enter a valid URL';
                      }
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                // --- Bio ---
                TextFormField(
                  controller: _bioController,
                  decoration: const InputDecoration(
                    labelText: 'Bio',
                    hintText: 'Tell us about yourself',
                    prefixIcon: Icon(Icons.article_outlined),
                    alignLabelWithHint: true,
                  ),
                  maxLines: 4,
                  maxLength: 1000,
                  textInputAction: TextInputAction.newline,
                ),
                const SizedBox(height: 16),

                // --- Timezone ---
                DropdownButtonFormField<String>(
                  initialValue: _selectedTimezone,
                  decoration: const InputDecoration(
                    labelText: 'Timezone',
                    prefixIcon: Icon(Icons.access_time),
                  ),
                  items: commonTimezones
                      .map((tz) => DropdownMenuItem(
                            value: tz,
                            child: Text(tz),
                          ))
                      .toList(),
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _selectedTimezone = value);
                    }
                  },
                ),
                const SizedBox(height: 32),

                // --- Save Button ---
                FilledButton.icon(
                  onPressed: _isSaving ? null : _save,
                  icon: _isSaving
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.save),
                  label: Text(_isSaving ? 'Saving...' : 'Save Changes'),
                ),
                const SizedBox(height: 16),
              ],
            ),
          );
        },
      ),
    );
  }
}
