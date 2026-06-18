import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/core/widgets/focusable_widget.dart';

class ProgressWidget extends StatelessWidget {
  final int value;
  final int? max;
  final ValueChanged<int> onChange;
  final bool isLoading;

  const ProgressWidget({
    super.key,
    required this.value,
    this.max,
    required this.onChange,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Decrement
        _roundButton(
          icon: Icons.remove,
          onTap: value > 0 ? () => onChange(value - 1) : null,
        ),
        const SizedBox(width: 8),
        // Value
        isLoading
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : Text(
                '$value',
                style: const TextStyle(
                  color: AppColors.textPrimary,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
        const SizedBox(width: 8),
        // Increment
        _roundButton(
          icon: Icons.add,
          onTap: max == null || value < max!
              ? () => onChange(value + 1)
              : null,
        ),
        const SizedBox(width: 4),
        if (max != null)
          Text(
            '/ $max',
            style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
          ),
      ],
    );
  }

  Widget _roundButton({required IconData icon, VoidCallback? onTap}) {
    return FocusableWidget(
      onPress: onTap,
      child: Container(
        width: 28,
        height: 28,
        decoration: BoxDecoration(
          color: onTap != null
              ? AppColors.accentPrimary.withValues(alpha: 0.2)
              : AppColors.borderDefault.withValues(alpha: 0.3),
          borderRadius: BorderRadius.circular(14),
        ),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(14),
          child: Icon(
            icon,
            size: 16,
            color: onTap != null ? AppColors.accentPrimary : AppColors.textMuted,
          ),
        ),
      ),
    );
  }
}
