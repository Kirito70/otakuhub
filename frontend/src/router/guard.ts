export interface GuardContext {
  toName: string | null
  requiresAuth: boolean
  setupRequired: boolean
  loggedInUser: boolean
}

export type GuardDecision = true | { name: 'setup' | 'discover' | 'login' }

export function resolveAccessGuard(context: GuardContext): GuardDecision {
  const { toName, requiresAuth, setupRequired, loggedInUser } = context

  if (setupRequired && toName !== 'setup') {
    return { name: 'setup' }
  }

  if (!setupRequired && toName === 'setup') {
    return loggedInUser ? { name: 'discover' } : { name: 'login' }
  }

  if (requiresAuth && !loggedInUser) {
    return { name: 'login' }
  }

  if ((toName === 'login' || toName === 'register') && loggedInUser) {
    return { name: 'discover' }
  }

  return true
}
