import { apiClient } from './client.js'

export function createAccountsApi(client = apiClient) {
  return {
    register({ username, firstName, lastName, password }) {
      return client.request('/api/accounts/register', {
        method: 'POST',
        body: JSON.stringify({ username, first_name: firstName, last_name: lastName, password }),
      })
    },
    login(username, password) {
      return client.request('/api/accounts/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })
    },
    get(userId) {
      return client.request(`/api/accounts/${userId}`)
    },
    update(userId, fields) {
      return client.request(`/api/accounts/${userId}`, {
        method: 'PATCH',
        body: JSON.stringify(fields),
      })
    },
    delete(userId) {
      return client.request(`/api/accounts/${userId}`, { method: 'DELETE' })
    },
  }
}

export const accountsApi = createAccountsApi()
