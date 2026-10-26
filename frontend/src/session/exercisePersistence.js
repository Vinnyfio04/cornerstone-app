import { readonly, ref } from 'vue'

import { sessionsApi } from '../api/sessions.js'

export function createExercisePersistence({
  getUser,
  plannedDurationMs = null,
  requests = sessionsApi,
  skill,
}) {
  const status = ref('idle')
  const error = ref(null)
  let sessionPromise = null
  let generation = 0

  function start() {
    if (sessionPromise) {
      return sessionPromise
    }

    const user = getUser()
    if (!user) {
      status.value = 'unsaved'
      return Promise.resolve(null)
    }

    const currentGeneration = ++generation
    status.value = 'starting'
    error.value = null
    sessionPromise = requests
      .start(user.id, skill, plannedDurationMs)
      .then((session) => {
        if (generation === currentGeneration) {
          status.value = 'active'
        }
        return session
      })
      .catch((requestError) => {
        if (generation === currentGeneration) {
          status.value = 'error'
          error.value = requestError
        }
        return null
      })
    return sessionPromise
  }

  async function finish(result) {
    const finishingSessionPromise = sessionPromise
    const finishingGeneration = generation
    sessionPromise = null
    const session = await (finishingSessionPromise ?? Promise.resolve(null))
    if (!session) {
      if (generation === finishingGeneration) {
        status.value = status.value === 'error' ? 'error' : 'unsaved'
      }
      return null
    }

    if (generation === finishingGeneration) {
      status.value = 'saving'
    }
    try {
      const savedSession = await requests.finish(session.id, result)
      if (generation === finishingGeneration) {
        status.value = 'saved'
      }
      return savedSession
    } catch (requestError) {
      if (generation === finishingGeneration) {
        status.value = 'error'
        error.value = requestError
      }
      return null
    }
  }

  function reset() {
    generation += 1
    status.value = 'idle'
    error.value = null
    sessionPromise = null
  }

  return {
    status: readonly(status),
    error: readonly(error),
    start,
    finish,
    reset,
  }
}
