import assert from 'node:assert/strict'
import test from 'node:test'

import { ApiError, createApiClient } from '../src/api/client.js'

function jsonResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    async json() {
      return body
    },
  }
}

test('returns data from the documented API envelope', async () => {
  const requests = []
  const client = createApiClient({
    baseUrl: 'http://cornerstone.test',
    async fetchImpl(url, options) {
      requests.push({ url, options })
      return jsonResponse(200, { data: { id: 7 }, error: null })
    },
  })

  const data = await client.request('/api/users/7')

  assert.deepEqual(data, { id: 7 })
  assert.equal(requests[0].url, 'http://cornerstone.test/api/users/7')
  assert.equal(requests[0].options.headers.Accept, 'application/json')
})

test('maps documented error envelopes to ApiError', async () => {
  const client = createApiClient({
    async fetchImpl() {
      return jsonResponse(504, {
        data: null,
        error: { code: 'model_timeout', message: 'The chat response timed out.' },
      })
    },
  })

  await assert.rejects(
    client.request('/api/chat/messages'),
    (error) =>
      error instanceof ApiError && error.code === 'model_timeout' && error.status === 504,
  )
})

test('maps transport failures without exposing network details', async () => {
  const client = createApiClient({
    async fetchImpl() {
      throw new TypeError('private socket detail')
    },
  })

  await assert.rejects(
    client.request('/api/health'),
    (error) => error instanceof ApiError && error.code === 'backend_unavailable',
  )
})
