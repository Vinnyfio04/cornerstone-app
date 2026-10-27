import assert from 'node:assert/strict'
import test from 'node:test'

import {
  appendLiveTranscriptDelta,
  createLiveTranscriptState,
  finalizeLiveTranscript,
  resetLiveTranscript,
} from '../src/voice/liveTranscript.js'

function transcriptEvent(type, delta, startMs, endMs) {
  return {
    type,
    delta,
    start_ms: startMs,
    end_ms: endMs,
  }
}

function startTranscript() {
  return createLiveTranscriptState({
    sessionId: 7,
    sessionStartedAtMs: Date.parse('2026-10-26T16:00:00.000Z'),
  })
}

test('appends assistant fragments exactly into one growing bubble', () => {
  let state = startTranscript()
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', 'I can', 0, 250),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', '  help help', 250, 600),
  )

  assert.equal(state.messages.length, 1)
  assert.equal(state.messages[0].content, 'I can  help help')
  assert.equal(state.messages[0].role, 'assistant')
  assert.equal(state.messages[0].transcript_status, 'streaming')
  assert.equal(state.messages[0].created_at, '2026-10-26T16:00:00.000Z')
})

test('interruption finishes the assistant bubble and fills a user bubble', () => {
  let state = startTranscript()
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', 'Take a slow', 0, 400),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', ' breath.', 400, 700),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', 'Wait', 650, 850),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', ', please.', 850, 1100),
  )

  assert.deepEqual(
    state.messages.map(({ role, content, transcript_status: status }) => ({
      role,
      content,
      status,
    })),
    [
      {
        role: 'assistant',
        content: 'Take a slow breath.',
        status: 'interrupted',
      },
      { role: 'user', content: 'Wait, please.', status: 'streaming' },
    ],
  )
})

test('assistant speech after user input always starts a new bubble', () => {
  let state = startTranscript()
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', 'First response', 0, 600),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', 'My interruption', 500, 1000),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', 'New response', 1100, 1450),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', ' continues', 1450, 1800),
  )

  assert.deepEqual(
    state.messages.map(({ role, content }) => ({ role, content })),
    [
      { role: 'assistant', content: 'First response' },
      { role: 'user', content: 'My interruption' },
      { role: 'assistant', content: 'New response continues' },
    ],
  )
})

test('uses timestamps to route late and overlapping fragments', () => {
  let state = startTranscript()
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', 'Hello', 0, 400),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', 'I am speaking', 500, 950),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', 'Sure', 1000, 1200),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', ' still', 950, 1250),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.output_transcript.delta', ' there', 350, 500),
  )

  assert.deepEqual(
    state.messages.map(({ role, content }) => ({ role, content })),
    [
      { role: 'assistant', content: 'Hello there' },
      { role: 'user', content: 'I am speaking still' },
      { role: 'assistant', content: 'Sure' },
    ],
  )
})

test('a long speech gap creates a new bubble for the same speaker', () => {
  let state = startTranscript()
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', 'Earlier thought.', 0, 400),
  )
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', 'Later thought.', 2500, 2800),
  )

  assert.deepEqual(
    state.messages.map(({ content, transcript_status: status }) => ({ content, status })),
    [
      { content: 'Earlier thought.', status: 'complete' },
      { content: 'Later thought.', status: 'streaming' },
    ],
  )
})

test('ignores malformed or oversized transcript events', () => {
  const state = startTranscript()
  const invalidEvents = [
    transcriptEvent('unknown', 'hello', 0, 1),
    transcriptEvent('session.input_transcript.delta', '', 0, 1),
    transcriptEvent('session.input_transcript.delta', 'hello', -1, 1),
    transcriptEvent('session.input_transcript.delta', 'hello', 2, 1),
    transcriptEvent('session.input_transcript.delta', 'x'.repeat(8001), 0, 1),
  ]

  for (const event of invalidEvents) {
    assert.equal(appendLiveTranscriptDelta(state, event), state)
  }
})

test('finalizes active bubbles and reset starts a fresh voice conversation', () => {
  let state = startTranscript()
  state = appendLiveTranscriptDelta(
    state,
    transcriptEvent('session.input_transcript.delta', 'Temporary transcript', 0, 300),
  )
  state = finalizeLiveTranscript(state)

  assert.equal(state.messages[0].transcript_status, 'complete')

  state = resetLiveTranscript(state, {
    sessionId: 8,
    sessionStartedAtMs: Date.parse('2026-10-26T16:01:00.000Z'),
  })
  assert.equal(state.sessionId, 8)
  assert.deepEqual(state.messages, [])
})

