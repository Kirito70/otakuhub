/// Simple date formatting utilities (replaces package:intl).
///
/// These are deliberately minimal — only what the Watch Party feature needs.
/// If more formatting is needed later, add `intl` to pubspec.yaml and migrate.

String formatDateShort(DateTime date) {
  return '${_monthAbbr(date.month)} ${date.day}, ${date.year}';
}

String formatDateFull(DateTime date) {
  final hour = date.hour > 12 ? date.hour - 12 : (date.hour == 0 ? 12 : date.hour);
  final minute = date.minute.toString().padLeft(2, '0');
  final amPm = date.hour >= 12 ? 'PM' : 'AM';
  final dayOfWeek = _dayOfWeek(date.weekday);
  return '$dayOfWeek, ${_monthAbbr(date.month)} ${date.day}, ${date.year} – $hour:$minute $amPm';
}

String _dayOfWeek(int weekday) {
  const days = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
  ];
  return days[weekday - 1];
}

String _monthAbbr(int month) {
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ];
  return months[month - 1];
}
