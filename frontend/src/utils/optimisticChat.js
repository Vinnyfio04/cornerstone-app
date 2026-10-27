export function createPendingUserMessage(content, pendingId, now = new Date()) {
  return {
    id: pendingId,
    role: 'user',
    content,
    delivery_status: 'pending',
    created_at: now.toISOString().replace('T', ' ').replace('Z', ''),
  }
}

export function reconcilePendingMessage(messages, pendingId, userMessage, assistantMessage) {
  const pendingIndex = messages.findIndex((message) => message.id === pendingId)
  if (pendingIndex < 0) {
    return [...messages, userMessage, assistantMessage]
  }

  const reconciled = [...messages]
  reconciled.splice(pendingIndex, 1, userMessage, assistantMessage)
  return reconciled
}

export function removePendingMessage(messages, pendingId) {
  return messages.filter((message) => message.id !== pendingId)
}
