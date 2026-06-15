import { ref, computed } from 'vue'

/**
 * Theme composable for OtakuHub.
 *
 * OtakuHub is a dark-only streaming app (aniwaves.ru-inspired).
 * The `isDark` flag is always true. We keep the composable interface
 * for backward compatibility with existing consumers.
 */
const _isDark = ref(true)

export function useTheme() {
  const isDark = computed(() => _isDark.value)

  function setDarkMode(enabled: boolean): void {
    _isDark.value = enabled
    document.documentElement.classList.toggle('dark', enabled)
  }

  function toggleDarkMode(): void {
    setDarkMode(!_isDark.value)
  }

  return {
    isDark,
    setDarkMode,
    toggleDarkMode,
  }
}
