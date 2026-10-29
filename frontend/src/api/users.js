import { apiClient } from './client.js'

export function createUsersApi(client = apiClient) {
  return {
    create(firstName, lastName, preferences = {}) {
      return client.request('/api/users', {
        method: 'POST',
        body: JSON.stringify({ first_name: firstName, last_name: lastName, preferences }),
      })
    },
    get(userId) {
      return client.request(`/api/users/${userId}`)
    },
    update(userId, fields) {
      return client.request(`/api/users/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify(fields),
      })
    },
    delete(userId) {
      return client.request(`/api/users/${userId}`, { method: 'DELETE' })
    },
  }
}

export const usersApi = createUsersApi()
