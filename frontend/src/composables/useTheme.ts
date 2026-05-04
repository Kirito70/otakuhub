import { computed } from 'vue'
import { useQuasar } from 'quasar'

export function useTheme() {
  const $q = useQuasar()

  const isDark = computed(() => $q.dark.isActive)

  function setDarkMode(enabled: boolean): void {
    $q.dark.set(enabled)
  }

  function toggleDarkMode(): void {
    $q.dark.toggle()
  }

  return {
    isDark,
    setDarkMode,
    toggleDarkMode,
  }
}
