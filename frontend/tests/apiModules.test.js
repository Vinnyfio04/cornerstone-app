import assert from 'node:assert/strict'
import test from 'node:test'

import { createChatApi } from '../src/api/chat.js'
import { createSessionsApi } from '../src/api/sessions.js'
import { createUsersApi } from '../src/api/users.js'
import { createVoiceApi } from '../src/api/voice.js'

function recordingClient() {
  const calls = []
  return {
    calls,
    request(path, options = {}) {
      calls.push({ path, options })
      return Promise.resolve({ ok: true })
    },
  }
}

test('maps the fictional user flow to the documented user endpoints', async () => {
  const client = recordingClient()
  const api = createUsersApi(client)

  await api.create('Fictional Demo User', { prototype_account: true })
  await api.update(4, { display_name: 'Updated Demo' })
  await api.get(4)

  assert.deepEqual(client.calls, [
    {
      path: '/api/users',
      options: {
        method: 'POST',
        body: JSON.stringify({
          display_name: 'Fictional Demo User',
          preferences: { prototype_account: true },
        }),
      },
    },
    {
      path: '/api/users/4',
      options: {
        method: 'PATCH',
        body: JSON.stringify({ display_name: 'Updated Demo' }),
      },
    },
    { path: '/api/users/4', options: {} },
  ])
})

test('maps measured exercise results to snake-case API fields', async () => {
  const client = recordingClient()
  const api = createSessionsApi(client)

  await api.start(3, 'paced_breathing', 60000)
  await api.finish(9, {
    status: 'exited',
    measuredActiveDurationMs: 18420,
    lastStep: 'inhale_cycle_2',
  })

  assert.deepEqual(JSON.parse(client.calls[0].options.body), {
    user_id: 3,
    skill: 'paced_breathing',
    planned_duration_ms: 60000,
  })
  assert.deepEqual(JSON.parse(client.calls[1].options.body), {
    status: 'exited',
    measured_active_duration_ms: 18420,
    last_step: 'inhale_cycle_2',
  })
})

test('maps new and continued messages to the documented chat endpoint', async () => {
  const client = recordingClient()
  const api = createChatApi(client)

  await api.send(2, 'Fictional scenario', null)
  await api.send(2, 'Continue', 7)

  assert.equal(client.calls[0].path, '/api/chat/messages')
  assert.deepEqual(JSON.parse(client.calls[0].options.body), {
    user_id: 2,
    conversation_id: null,
    content: 'Fictional scenario',
  })
  assert.deepEqual(JSON.parse(client.calls[1].options.body), {
    user_id: 2,
    conversation_id: 7,
    content: 'Continue',
  })
})

test('maps voice configuration and SDP exchange to the documented endpoints', async () => {
  const client = recordingClient()
  const api = createVoiceApi(client)

  await api.getConfig()
  await api.createSession('v=0\r\nm=audio 9 RTP/AVP 0\r\n')

  assert.deepEqual(client.calls, [
    { path: '/api/voice/config', options: {} },
    {
      path: '/api/voice/sessions',
      options: {
        method: 'POST',
        body: JSON.stringify({ sdp_offer: 'v=0\r\nm=audio 9 RTP/AVP 0\r\n' }),
      },
    },
  ])
})
