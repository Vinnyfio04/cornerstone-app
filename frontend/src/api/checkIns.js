import { apiClient } from './client.js'

export function createCheckInsApi(client = apiClient) {
  return {
    create(userId, { feeling, color, description, checkInDate }) {
      return client.request('/api/check-ins', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          feeling,
          color,
          description,
          check_in_date: checkInDate,
        }),
      })
    },
    list(userId) {
      return client.request(`/api/users/${userId}/check-ins`)
    },
    update(checkInId, { feeling, color, description }) {
      return client.request(`/api/check-ins/${checkInId}`, {
        method: 'PATCH',
        body: JSON.stringify({ feeling, color, description }),
      })
    },
  }
}

export const checkInsApi = createCheckInsApi()
