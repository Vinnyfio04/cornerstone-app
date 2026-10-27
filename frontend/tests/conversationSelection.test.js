import assert from 'node:assert/strict'
import test from 'node:test'

import {
  parseConversationId,
  selectConversation,
} from '../src/utils/conversationSelection.js'

const conversations = [
  { id: 8, updated_at: '2026-10-27 12:00:00' },
  { id: 3, updated_at: '2026-10-26 12:00:00' },
]

test('parses only positive integer conversation query values', () => {
  assert.equal(parseConversationId('8'), 8)
  assert.equal(parseConversationId(['3', '8']), 3)
  assert.equal(parseConversationId('0'), null)
  assert.equal(parseConversationId('-1'), null)
  assert.equal(parseConversationId('3.5'), null)
  assert.equal(parseConversationId(undefined), null)
})

test('selects an explicitly requested saved conversation', () => {
  assert.deepEqual(selectConversation(conversations, { requestedId: '3' }), {
    status: 'selected',
    conversation: conversations[1],
  })
})

test('reports an unavailable or invalid saved conversation', () => {
  assert.equal(
    selectConversation(conversations, { requestedId: '99' }).status,
    'unavailable',
  )
  assert.equal(
    selectConversation(conversations, { requestedId: 'invalid' }).status,
    'unavailable',
  )
})

test('defaults to the newest summary and supports an explicit fresh conversation', () => {
  assert.equal(selectConversation(conversations).conversation.id, 8)
  assert.deepEqual(selectConversation(conversations, { startNew: true }), {
    status: 'new',
    conversation: null,
  })
  assert.equal(selectConversation([]).status, 'new')
})

