import 'package:flutter/material.dart';
import 'package:otakuhub/core/theme/app_colors.dart';
import 'package:otakuhub/core/widgets/focusable_widget.dart';

class ScoreWidget extends StatelessWidget {
  final double? value;
  final ValueChanged<double?> onChange;
  final bool isLoading;

  const ScoreWidget({
    super.key,
    this.value,
    required this.onChange,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const SizedBox(
        width: 20,
        height: 20,
        child: CircularProgressIndicator(strokeWidth: 2),
      );
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Star icons (0-10 scale, each star = 2 points)
        ...List.generate(5, (i) {
          final starValue = (i + 1) * 2;
          final filled = value != null && value! >= starValue;
          final half = value != null && value! >= starValue - 1 && value! < starValue;
          return FocusableWidget(
            onPress: () {
              if (value == starValue) {
                onChange(null);
              } else {
                onChange(starValue.toDouble());
              }
            },
            child: Padding(
              padding: const EdgeInsets.only(right: 2),
              child: Icon(
                filled
                    ? Icons.star
                    : half
                        ? Icons.star_half
                        : Icons.star_border,
                size: 20,
                color: filled || half
                    ? const Color(0xFFF59E0B)
                    : AppColors.textMuted,
              ),
            ),
          );
        }),
        // Score text
        if (value != null) ...[
          const SizedBox(width: 4),
          Text(
            value!.toStringAsFixed(1),
            style: const TextStyle(
              color: AppColors.textPrimary,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ],
    );
  }
}
