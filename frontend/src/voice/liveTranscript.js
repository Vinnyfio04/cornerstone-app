const MAX_TRANSCRIPT_DELTA_LENGTH = 8000
const SPEAKER_GAP_MS = 1800

const TRANSCRIPT_EVENT_ROLES = Object.freeze({
  'session.input_transcript.delta': 'user',
  'session.output_transcript.delta': 'assistant',
})

function copyState(state, messages = state.messages) {
  return {
    ...state,
    messages,
  }
}

function isValidTimestamp(value) {
  return Number.isFinite(value) && value >= 0
}

function normalizeDelta(event) {
  const role = TRANSCRIPT_EVENT_ROLES[event?.type]
  if (
    !role ||
    typeof event.delta !== 'string' ||
    event.delta.length === 0 ||
    event.delta.length > MAX_TRANSCRIPT_DELTA_LENGTH ||
    !isValidTimestamp(event.start_ms) ||
    !isValidTimestamp(event.end_ms) ||
    event.end_ms < event.start_ms
  ) {
    return null
  }

  return {
    role,
    delta: event.delta,
    startMs: event.start_ms,
    endMs: event.end_ms,
  }
}

function completeMessage(message, status = 'complete') {
  if (message.transcript_status !== 'streaming') {
    return message
  }

  return {
    ...message,
    transcript_status: status,
  }
}

function sortMessages(messages) {
  return messages.toSorted(
    (left, right) => left.start_ms - right.start_ms || left.sequence - right.sequence,
  )
}

function findTimelineMessage(messages, role, startMs) {
  const sameRole = messages
    .filter((message) => message.role === role)
    .toSorted(
      (left, right) => left.start_ms - right.start_ms || left.sequence - right.sequence,
    )

  let candidate = null
  for (const message of sameRole) {
    if (message.start_ms > startMs) {
      break
    }
    candidate = message
  }
  return candidate
}

function hasUserBarrier(messages, assistantMessage, startMs) {
  return messages.some(
    (message) =>
      message.role === 'user' &&
      message.start_ms > assistantMessage.start_ms &&
      message.start_ms <= startMs,
  )
}

function shouldStartNewMessage(messages, candidate, role, startMs) {
  if (!candidate) {
    return true
  }

  if (startMs - candidate.end_ms > SPEAKER_GAP_MS) {
    return true
  }

  return role === 'assistant' && hasUserBarrier(messages, candidate, startMs)
}

function appendToMessage(message, delta, startMs, endMs) {
  return {
    ...message,
    content: `${message.content}${delta}`,
    start_ms: Math.min(message.start_ms, startMs),
    end_ms: Math.max(message.end_ms, endMs),
  }
}

function createMessage(state, delta) {
  const sequence = state.nextSequence
  const createdAtMs = state.sessionStartedAtMs + delta.startMs

  return {
    id: `voice-${state.sessionId}-${sequence}`,
    role: delta.role,
    content: delta.delta,
    delivery_status: 'delivered',
    source: 'voice',
    transcript_status: 'streaming',
    start_ms: delta.startMs,
    end_ms: delta.endMs,
    sequence,
    created_at: new Date(createdAtMs).toISOString(),
  }
}

export function createLiveTranscriptState({
  sessionId = 0,
  sessionStartedAtMs = 0,
} = {}) {
  return {
    sessionId,
    sessionStartedAtMs,
    nextSequence: 1,
    messages: [],
  }
}

export function resetLiveTranscript(_state, { sessionId, sessionStartedAtMs }) {
  return createLiveTranscriptState({ sessionId, sessionStartedAtMs })
}

export function appendLiveTranscriptDelta(state, event) {
  const delta = normalizeDelta(event)
  if (!delta) {
    return state
  }

  let messages = state.messages
  if (delta.role === 'user') {
    messages = messages.map((message) => {
      if (
        message.role === 'assistant' &&
        message.transcript_status === 'streaming' &&
        message.start_ms <= delta.startMs
      ) {
        return completeMessage(message, 'interrupted')
      }
      return message
    })
  }

  const candidate = findTimelineMessage(messages, delta.role, delta.startMs)
  if (!shouldStartNewMessage(messages, candidate, delta.role, delta.startMs)) {
    const nextMessages = messages.map((message) =>
      message.id === candidate.id
        ? appendToMessage(message, delta.delta, delta.startMs, delta.endMs)
        : message,
    )
    return copyState(state, sortMessages(nextMessages))
  }

  messages = messages.map((message) => {
    if (message.role === delta.role && message.transcript_status === 'streaming') {
      return completeMessage(message)
    }
    return message
  })

  const message = createMessage(state, delta)
  return {
    ...state,
    nextSequence: state.nextSequence + 1,
    messages: sortMessages([...messages, message]),
  }
}

export function finalizeLiveTranscript(state) {
  const messages = state.messages.map((message) => completeMessage(message))
  if (messages.every((message, index) => message === state.messages[index])) {
    return state
  }
  return copyState(state, messages)
}

