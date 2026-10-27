import assert from 'node:assert/strict'
import test from 'node:test'

import {
  createPendingUserMessage,
  reconcilePendingMessage,
  removePendingMessage,
} from '../src/utils/optimisticChat.js'

test('creates an immediately renderable pending user message', () => {
  const message = createPendingUserMessage(
    'Hello',
    'pending-1',
    new Date('2026-10-27T12:34:56.000Z'),
  )

  assert.deepEqual(message, {
    id: 'pending-1',
    role: 'user',
    content: 'Hello',
    delivery_status: 'pending',
    created_at: '2026-10-27 12:34:56.000',
  })
})

test('reconciles the pending bubble without duplicating the user message', () => {
  const previous = { id: 4, role: 'assistant', content: 'Earlier' }
  const pending = createPendingUserMessage('Hello', 'pending-2')
  const savedUser = { id: 5, role: 'user', content: 'Hello', delivery_status: 'delivered' }
  const savedAssistant = {
    id: 6,
    role: 'assistant',
    content: 'Hello. How can I help?',
    delivery_status: 'delivered',
  }

  const messages = reconcilePendingMessage(
    [previous, pending],
    pending.id,
    savedUser,
    savedAssistant,
  )

  assert.deepEqual(messages, [previous, savedUser, savedAssistant])
  assert.equal(messages.filter((message) => message.role === 'user').length, 1)
})

test('keeps a completed response if the pending bubble was already removed', () => {
  const savedUser = { id: 7, role: 'user', content: 'Hello', delivery_status: 'delivered' }
  const savedAssistant = {
    id: 8,
    role: 'assistant',
    content: 'Hi',
    delivery_status: 'delivered',
  }

  assert.deepEqual(
    reconcilePendingMessage([], 'pending-missing', savedUser, savedAssistant),
    [savedUser, savedAssistant],
  )
})

test('removes a failed pending bubble before persisted recovery loads', () => {
  const previous = { id: 9, role: 'assistant', content: 'Earlier' }
  const pending = createPendingUserMessage('Hello', 'pending-failed')

  assert.deepEqual(removePendingMessage([previous, pending], pending.id), [previous])
})
