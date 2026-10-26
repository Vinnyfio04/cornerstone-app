import assert from 'node:assert/strict'
import test from 'node:test'

import { ApiError } from '../src/api/client.js'
import {
  DEFAULT_DEMO_NAME,
  DEMO_USER_ID_KEY,
  resolveDemoUser,
} from '../src/session/demoUser.js'

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

test('creates and remembers the fictional demo user', async () => {
  const storage = memoryStorage()
  const calls = []
  const user = await resolveDemoUser({
    storage,
    requests: {
      async create(displayName, preferences) {
        calls.push({ displayName, preferences })
        return { id: 4, display_name: displayName, preferences }
      },
    },
  })

  assert.equal(user.id, 4)
  assert.equal(storage.getItem(DEMO_USER_ID_KEY), '4')
  assert.deepEqual(calls, [
    { displayName: DEFAULT_DEMO_NAME, preferences: { prototype_account: true } },
  ])
})

test('recovers the remembered user without creating a duplicate', async () => {
  const storage = memoryStorage({ [DEMO_USER_ID_KEY]: '9' })
  let createCalled = false
  const user = await resolveDemoUser({
    storage,
    requests: {
      async get(userId) {
        return { id: userId, display_name: DEFAULT_DEMO_NAME }
      },
      async create() {
        createCalled = true
      },
    },
  })

  assert.equal(user.id, 9)
  assert.equal(createCalled, false)
})

test('replaces a stale remembered identifier after not_found', async () => {
  const storage = memoryStorage({ [DEMO_USER_ID_KEY]: '12' })
  const user = await resolveDemoUser({
    storage,
    requests: {
      async get() {
        throw new ApiError('missing', { code: 'not_found', status: 404 })
      },
      async create() {
        return { id: 13, display_name: DEFAULT_DEMO_NAME }
      },
    },
  })

  assert.equal(user.id, 13)
  assert.equal(storage.getItem(DEMO_USER_ID_KEY), '13')
})
