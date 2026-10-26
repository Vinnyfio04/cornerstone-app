import { apiClient } from './client.js'

export function createSessionsApi(client = apiClient) {
  return {
    start(userId, skill, plannedDurationMs = null) {
      return client.request('/api/exercise-sessions', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          skill,
          planned_duration_ms: plannedDurationMs,
        }),
      })
    },
    finish(sessionId, result) {
      return client.request(`/api/exercise-sessions/${sessionId}`, {
        method: 'PATCH',
        body: JSON.stringify({
          status: result.status,
          measured_active_duration_ms: result.measuredActiveDurationMs,
          last_step: result.lastStep,
        }),
      })
    },
    list(userId) {
      return client.request(`/api/users/${userId}/exercise-sessions`)
    },
  }
}

export const sessionsApi = createSessionsApi()
