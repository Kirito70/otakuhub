import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_tokens.dart';

/// ADR 094 — FriendAvatar: circular avatar with active ring.
///
/// Ring = accent.mint if active (last 5 min), else transparent.
/// Fallback: initials on deterministic brand color.
/// Stackable via [AvatarStack] for +N overflow.
class FriendAvatar extends StatelessWidget {
  final String? imageUrl;
  final String? displayName;
  final bool isActive;
  final double radius;

  const FriendAvatar({
    super.key,
    this.imageUrl,
    this.displayName,
    this.isActive = false,
    this.radius = 18,
  });

  static const _brandColors = [
    Color(0xFF7C5CFC),
    Color(0xFFFF6E8A),
    Color(0xFF2FD9A8),
    Color(0xFF5AB0FF),
    Color(0xFFFFB454),
    Color(0xFF3FD0D9),
    Color(0xFF7FD957),
    Color(0xFFFF5C6C),
  ];

  Color _deterministicColor(String name) {
    final hash = name.hashCode.abs();
    return _brandColors[hash % _brandColors.length];
  }

  String _initials(String name) {
    final parts = name.trim().split(RegExp(r'\s+'));
    if (parts.length >= 2) {
      return '${parts.first[0]}${parts.last[0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final diameter = radius * 2;

    return Container(
      width: diameter + 4, // +4 for ring
      height: diameter + 4,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: isActive ? tokens.accentMint : Colors.transparent,
      ),
      padding: const EdgeInsets.all(2),
      child: ClipOval(
        child: imageUrl != null
            ? Image.network(
                imageUrl!,
                width: diameter,
                height: diameter,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) => _fallback(diameter),
              )
            : _fallback(diameter),
      ),
    );
  }

  Widget _fallback(double diameter) {
    final name = displayName ?? '?';
    return Container(
      width: diameter,
      height: diameter,
      color: _deterministicColor(name),
      alignment: Alignment.center,
      child: Text(
        _initials(name),
        style: TextStyle(
          fontFamily: 'Plus Jakarta Sans',
          fontSize: radius * 0.6,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
      ),
    );
  }
}

/// A stacked row of [FriendAvatar]s with optional +N overflow indicator.
class AvatarStack extends StatelessWidget {
  final List<Widget> avatars;
  final int maxVisible;
  final double overlap;
  final double avatarRadius;

  const AvatarStack({
    super.key,
    required this.avatars,
    this.maxVisible = 3,
    this.overlap = 8,
    this.avatarRadius = 16,
  });

  @override
  Widget build(BuildContext context) {
    final tokens = context.tokens;
    final visible = avatars.take(maxVisible).toList();
    final overflow = avatars.length - maxVisible;

    return SizedBox(
      height: (avatarRadius + 2) * 2,
      child: Stack(
        children: [
          for (var i = 0; i < visible.length; i++)
            Positioned(
              left: i * (avatarRadius * 2 - overlap),
              child: visible[i],
            ),
          if (overflow > 0)
            Positioned(
              left: visible.length * (avatarRadius * 2 - overlap),
              child: Container(
                width: (avatarRadius + 2) * 2,
                height: (avatarRadius + 2) * 2,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: tokens.bgSurfaceAlt,
                  border: Border.all(color: tokens.borderSubtle),
                ),
                alignment: Alignment.center,
                child: Text(
                  '+$overflow',
                  style: TextStyle(
                    fontFamily: 'Plus Jakarta Sans',
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: tokens.textSecondary,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
