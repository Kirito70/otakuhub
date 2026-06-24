import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';

class ProfileAvatar extends StatelessWidget {
  final double size;
  final String? imageUrl;
  final String? displayName;
  final String username;

  const ProfileAvatar({
    super.key,
    this.size = 80,
    this.imageUrl,
    this.displayName,
    required this.username,
  });

  String get _initial {
    final source = displayName ?? username;
    if (source.isNotEmpty) {
      return source[0].toUpperCase();
    }
    return '?';
  }

  @override
  Widget build(BuildContext context) {
    final avatarLabel = displayName ?? username;

    if (imageUrl != null && imageUrl!.isNotEmpty) {
      return Semantics(
        label: avatarLabel,
        child: CircleAvatar(
          radius: size / 2,
          backgroundImage: NetworkImage(imageUrl!),
          onBackgroundImageError: (_, __) => _buildFallback(),
        ),
      );
    }
    return Semantics(
      label: avatarLabel,
      child: _buildFallback(),
    );
  }

  Widget _buildFallback() {
    return CircleAvatar(
      radius: size / 2,
      backgroundColor: AppColors.accentPrimary.withAlpha(40),
      child: Text(
        _initial,
        style: TextStyle(
          fontSize: size * 0.45,
          fontWeight: FontWeight.bold,
          color: AppColors.accentPrimary,
        ),
      ),
    );
  }
}
