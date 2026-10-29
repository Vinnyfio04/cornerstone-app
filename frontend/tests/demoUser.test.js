import assert from 'node:assert/strict'
import test from 'node:test'

import { ApiError } from '../src/api/client.js'
import {
  ACCOUNT_USER_ID_KEY,
  createAccountSession,
  resolveStoredAccount,
} from '../src/session/accountSession.js'

function memoryStorage(initial = {}) {
  const values = new Map(Object.entries(initial))
  return {
    getItem(key) {
      return values.get(key) ?? null
    },
    setItem(key, value) {
      values.set(key, value)
    },
    removeItem(key) {
      values.delete(key)
    },
  }
}

test('stays signed out when local storage has no account', async () => {
  const storage = memoryStorage()
  const account = await resolveStoredAccount({
    storage,
    requests: {
      async get() {
        throw new Error('must not be called')
      },
    },
  })

  assert.equal(account, null)
})

test('recovers the remembered signed-in account', async () => {
  const storage = memoryStorage({ [ACCOUNT_USER_ID_KEY]: '9' })
  const account = await resolveStoredAccount({
    storage,
    requests: {
      async get(userId) {
        return {
          id: userId,
          username: 'account-user',
          first_name: 'Account',
          last_name: 'User',
        }
      },
    },
  })

  assert.equal(account.id, 9)
})

test('clears a stale remembered identifier after not_found', async () => {
  const storage = memoryStorage({ [ACCOUNT_USER_ID_KEY]: '12' })
  const account = await resolveStoredAccount({
    storage,
    requests: {
      async get() {
        throw new ApiError('missing', { code: 'not_found', status: 404 })
      },
    },
  })

  assert.equal(account, null)
  assert.equal(storage.getItem(ACCOUNT_USER_ID_KEY), null)
})

test('registers, remembers, updates, and logs out without storing credentials', async () => {
  const storage = memoryStorage()
  const session = createAccountSession({
    storage,
    requests: {
      async register() {
        return { id: 4, username: 'new-user', first_name: 'New', last_name: 'User' }
      },
      async update(userId, fields) {
        return {
          id: userId,
          username: fields.username,
          first_name: fields.first_name,
          last_name: fields.last_name,
        }
      },
    },
  })

  await session.register({
    username: 'new-user',
    firstName: 'New',
    lastName: 'User',
    password: 'private-password',
  })
  assert.equal(storage.getItem(ACCOUNT_USER_ID_KEY), '4')
  assert.equal(storage.getItem('password'), null)

  await session.updateAccount({
    username: 'updated',
    first_name: 'Updated',
    last_name: 'User',
  })
  assert.equal(session.user.value.first_name, 'Updated')

  session.logout()
  assert.equal(session.user.value, null)
  assert.equal(storage.getItem(ACCOUNT_USER_ID_KEY), null)
})
