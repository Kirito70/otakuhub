import { describe, expect, it } from 'vitest'

import { useValidationRules } from '../useValidationRules'

describe('useValidationRules', () => {
  const rules = useValidationRules()

  it('validates required and minLength', () => {
    expect(rules.required('Name')('')).toBe('Name is required')
    expect(rules.minLength('Name', 3)('ab')).toBe('Name must be at least 3 characters')
    expect(rules.minLength('Name', 3)('abcd')).toBe(true)
  })

  it('validates email format', () => {
    expect(rules.email('Email')('bad')).toBe('Enter a valid email address')
    expect(rules.email('Email')('test@example.com')).toBe(true)
  })

  it('validates optional HTTP URL', () => {
    expect(rules.isHttpUrl('Stream URL')('')).toBe(true)
    expect(rules.isHttpUrl('Stream URL')('ftp://example.com')).toBe('Stream URL must start with http:// or https://')
    expect(rules.isHttpUrl('Stream URL')('https://example.com')).toBe(true)
  })
})
