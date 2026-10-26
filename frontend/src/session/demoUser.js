import { inject, readonly, ref } from 'vue'

import { ApiError } from '../api/client.js'
import { usersApi } from '../api/users.js'

export const DEMO_USER_ID_KEY = 'cornerstone.fictionalDemoUserId'
export const DEFAULT_DEMO_NAME = 'Fictional Demo User'

const demoUserSessionKey = Symbol('cornerstone-demo-user-session')

function readStoredUserId(storage) {
  const value = storage?.getItem(DEMO_USER_ID_KEY)
  const userId = Number.parseInt(value ?? '', 10)
  return Number.isInteger(userId) && userId > 0 ? userId : null
}

export async function resolveDemoUser({ storage, requests = usersApi }) {
  const storedUserId = readStoredUserId(storage)

  if (storedUserId !== null) {
    try {
      return await requests.get(storedUserId)
    } catch (error) {
      if (!(error instanceof ApiError) || error.code !== 'not_found') {
        throw error
      }
      storage?.removeItem(DEMO_USER_ID_KEY)
    }
  }

  const user = await requests.create(DEFAULT_DEMO_NAME, { prototype_account: true })
  storage?.setItem(DEMO_USER_ID_KEY, String(user.id))
  return user
}

export function createDemoUserSession({ storage = globalThis.localStorage, requests = usersApi } = {}) {
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  let initializationPromise = null

  async function initialize({ force = false } = {}) {
    if (initializationPromise && !force) {
      return initializationPromise
    }

    isLoading.value = true
    error.value = null
    initializationPromise = resolveDemoUser({ storage, requests })
      .then((resolvedUser) => {
        user.value = resolvedUser
        return resolvedUser
      })
      .catch((requestError) => {
        error.value = requestError
        throw requestError
      })
      .finally(() => {
        isLoading.value = false
        initializationPromise = null
      })

    return initializationPromise
  }

  async function updateDisplayName(displayName) {
    if (!user.value) {
      throw new ApiError('The fictional demo user is not ready.')
    }
    user.value = await requests.update(user.value.id, { display_name: displayName })
    return user.value
  }

  return {
    user: readonly(user),
    isLoading: readonly(isLoading),
    error: readonly(error),
    initialize,
    updateDisplayName,
  }
}

export function provideDemoUserSession(app, session) {
  app.provide(demoUserSessionKey, session)
}

export function useDemoUserSession() {
  const session = inject(demoUserSessionKey)
  if (!session) {
    throw new Error('Demo user session was not provided')
  }
  return session
}
