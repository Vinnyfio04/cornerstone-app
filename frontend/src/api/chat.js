import { apiClient } from './client.js'

export function createChatApi(client = apiClient) {
  return {
    send(userId, content, conversationId = null) {
      return client.request('/api/chat/messages', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          conversation_id: conversationId,
          content,
        }),
      })
    },
    listConversations(userId) {
      return client.request(`/api/users/${userId}/conversations`)
    },
    listMessages(conversationId) {
      return client.request(`/api/conversations/${conversationId}/messages`)
    },
  }
}

export const chatApi = createChatApi()
