import { inject, readonly, ref } from 'vue'

import { accountsApi } from '../api/accounts.js'
import { ApiError } from '../api/client.js'

export const ACCOUNT_USER_ID_KEY = 'cornerstone.accountUserId'

const accountSessionKey = Symbol('cornerstone-account-session')

function readStoredUserId(storage) {
  const value = storage?.getItem(ACCOUNT_USER_ID_KEY)
  const userId = Number.parseInt(value ?? '', 10)
  return Number.isInteger(userId) && userId > 0 ? userId : null
}

export async function resolveStoredAccount({ storage, requests = accountsApi }) {
  const storedUserId = readStoredUserId(storage)
  if (storedUserId === null) {
    return null
  }

  try {
    return await requests.get(storedUserId)
  } catch (error) {
    if (error instanceof ApiError && error.code === 'not_found') {
      storage?.removeItem(ACCOUNT_USER_ID_KEY)
      return null
    }
    throw error
  }
}

export function createAccountSession({ storage = globalThis.localStorage, requests = accountsApi } = {}) {
  const user = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  let initializationPromise = null

  function remember(account) {
    user.value = account
    storage?.setItem(ACCOUNT_USER_ID_KEY, String(account.id))
    error.value = null
    return account
  }

  function clear() {
    user.value = null
    storage?.removeItem(ACCOUNT_USER_ID_KEY)
  }

  async function initialize({ force = false } = {}) {
    if (initializationPromise && !force) {
      return initializationPromise
    }

    isLoading.value = true
    error.value = null
    initializationPromise = resolveStoredAccount({ storage, requests })
      .then((account) => {
        user.value = account
        return account
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

  async function register(fields) {
    return remember(await requests.register(fields))
  }

  async function login(username, password) {
    return remember(await requests.login(username, password))
  }

  function logout() {
    clear()
  }

  async function updateAccount(fields) {
    if (!user.value) {
      throw new ApiError('Sign in before changing an account.', { code: 'sign_in_required' })
    }
    return remember(await requests.update(user.value.id, fields))
  }

  async function deleteAccount() {
    if (!user.value) {
      throw new ApiError('Sign in before deleting an account.', { code: 'sign_in_required' })
    }
    await requests.delete(user.value.id)
    clear()
  }

  return {
    user: readonly(user),
    isLoading: readonly(isLoading),
    error: readonly(error),
    initialize,
    register,
    login,
    logout,
    updateAccount,
    deleteAccount,
  }
}

export function provideAccountSession(app, session) {
  app.provide(accountSessionKey, session)
}

export function useAccountSession() {
  const session = inject(accountSessionKey)
  if (!session) {
    throw new Error('Account session was not provided')
  }
  return session
}
