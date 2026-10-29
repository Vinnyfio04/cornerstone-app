import assert from 'node:assert/strict'
import test from 'node:test'

import { createAccountsApi } from '../src/api/accounts.js'
import { createChatApi } from '../src/api/chat.js'
import { createCheckInsApi } from '../src/api/checkIns.js'
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

test('maps account registration, login, update, and deletion to account endpoints', async () => {
  const client = recordingClient()
  const api = createAccountsApi(client)

  await api.register({
    username: 'account-user',
    firstName: 'Account',
    lastName: 'User',
    password: 'password-1',
  })
  await api.login('account-user', 'password-1')
  await api.get(4)
  await api.update(4, { first_name: 'Updated', last_name: 'User' })
  await api.delete(4)

  assert.deepEqual(client.calls, [
    {
      path: '/api/accounts/register',
      options: {
        method: 'POST',
        body: JSON.stringify({
          username: 'account-user',
          first_name: 'Account',
          last_name: 'User',
          password: 'password-1',
        }),
      },
    },
    {
      path: '/api/accounts/login',
      options: {
        method: 'POST',
        body: JSON.stringify({ username: 'account-user', password: 'password-1' }),
      },
    },
    { path: '/api/accounts/4', options: {} },
    {
      path: '/api/accounts/4',
      options: {
        method: 'PATCH',
        body: JSON.stringify({ first_name: 'Updated', last_name: 'User' }),
      },
    },
    { path: '/api/accounts/4', options: { method: 'DELETE' } },
  ])
})

test('maps the fictional user flow to the documented user endpoints', async () => {
  const client = recordingClient()
  const api = createUsersApi(client)

  await api.create('Fictional', 'Demo User', { prototype_account: true })
  await api.update(4, { first_name: 'Updated', last_name: 'Demo' })
  await api.get(4)

  assert.deepEqual(client.calls, [
    {
      path: '/api/users',
      options: {
        method: 'POST',
        body: JSON.stringify({
          first_name: 'Fictional',
          last_name: 'Demo User',
          preferences: { prototype_account: true },
        }),
      },
    },
    {
      path: '/api/users/4',
      options: {
        method: 'PATCH',
        body: JSON.stringify({ first_name: 'Updated', last_name: 'Demo' }),
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

test('maps calendar check-ins to the documented endpoints', async () => {
  const client = recordingClient()
  const api = createCheckInsApi(client)

  await api.create(3, {
    feeling: 'happy',
    color: '#d2a13f',
    description: 'A good day.',
    checkInDate: '2026-10-28',
  })
  await api.list(3)
  await api.update(7, {
    feeling: 'hopeful',
    color: '#496db2',
    description: 'The day improved.',
  })

  assert.deepEqual(client.calls, [
    {
      path: '/api/check-ins',
      options: {
        method: 'POST',
        body: JSON.stringify({
          user_id: 3,
          feeling: 'happy',
          color: '#d2a13f',
          description: 'A good day.',
          check_in_date: '2026-10-28',
        }),
      },
    },
    { path: '/api/users/3/check-ins', options: {} },
    {
      path: '/api/check-ins/7',
      options: {
        method: 'PATCH',
        body: JSON.stringify({
          feeling: 'hopeful',
          color: '#496db2',
          description: 'The day improved.',
        }),
      },
    },
  ])
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
