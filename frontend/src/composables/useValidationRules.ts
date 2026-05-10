export type ValidationRule = (value: string) => true | string

function required(label: string): ValidationRule {
  return (value: string) => (value.trim().length > 0 ? true : `${label} is required`)
}

function minLength(label: string, min: number): ValidationRule {
  return (value: string) => (value.trim().length >= min ? true : `${label} must be at least ${min} characters`)
}

function email(label = 'Email'): ValidationRule {
  const regex = /.+@.+\..+/
  return (value: string) => (regex.test(value.trim()) ? true : `Enter a valid ${label.toLowerCase()} address`)
}

function matches(label: string, getExpected: () => string, mismatchMessage: string): ValidationRule {
  return (value: string) => (value === getExpected() ? true : mismatchMessage)
}

function isHttpUrl(label: string): ValidationRule {
  return (value: string) => {
    const trimmed = value.trim()
    if (!trimmed) {
      return true
    }

    try {
      const parsed = new URL(trimmed)
      return ['http:', 'https:'].includes(parsed.protocol) ? true : `${label} must start with http:// or https://`
    } catch {
      return `${label} must be a valid URL`
    }
  }
}

export function useValidationRules() {
  return {
    required,
    minLength,
    email,
    matches,
    isHttpUrl,
  }
}
