export function parseConversationId(value) {
  const candidate = Array.isArray(value) ? value[0] : value
  if (typeof candidate !== 'string' || !/^\d+$/.test(candidate)) {
    return null
  }

  const id = Number(candidate)
  return Number.isSafeInteger(id) && id > 0 ? id : null
}

export function selectConversation(conversations, { requestedId, startNew = false } = {}) {
  if (startNew) {
    return { status: 'new', conversation: null }
  }

  if (requestedId !== undefined) {
    const id = parseConversationId(requestedId)
    const conversation = conversations.find((item) => item.id === id)
    return conversation
      ? { status: 'selected', conversation }
      : { status: 'unavailable', conversation: null }
  }

  return conversations.length > 0
    ? { status: 'selected', conversation: conversations[0] }
    : { status: 'new', conversation: null }
}

