import { describe, expect, it } from 'vitest'

import { resolveAccessGuard } from '../guard'

describe('resolveAccessGuard', () => {
  it('redirects to setup when setup is required', () => {
    expect(resolveAccessGuard({ toName: 'discover', requiresAuth: true, setupRequired: true, loggedInUser: false })).toEqual({ name: 'setup' })
  })

  it('redirects away from setup when setup is complete', () => {
    expect(resolveAccessGuard({ toName: 'setup', requiresAuth: false, setupRequired: false, loggedInUser: false })).toEqual({ name: 'login' })
    expect(resolveAccessGuard({ toName: 'setup', requiresAuth: false, setupRequired: false, loggedInUser: true })).toEqual({ name: 'discover' })
  })

  it('guards deep links requiring auth', () => {
    expect(resolveAccessGuard({ toName: 'media-detail', requiresAuth: true, setupRequired: false, loggedInUser: false })).toEqual({ name: 'login' })
  })

  it('allows auth screens only for logged-out users', () => {
    expect(resolveAccessGuard({ toName: 'login', requiresAuth: false, setupRequired: false, loggedInUser: true })).toEqual({ name: 'discover' })
    expect(resolveAccessGuard({ toName: 'register', requiresAuth: false, setupRequired: false, loggedInUser: true })).toEqual({ name: 'discover' })
  })
})
