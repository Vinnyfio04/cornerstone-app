<script setup>
import { ref, watch } from 'vue'

import { sessionsApi } from '../api/sessions.js'
import { useAccountSession } from '../session/accountSession.js'

const accountSession = useAccountSession()
const exerciseSessions = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

function formatDuration(durationMs) {
  if (!Number.isFinite(durationMs)) {
    return 'Not recorded'
  }
  const seconds = Math.round(durationMs / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainder = seconds % 60
  return minutes > 0 ? `${minutes}m ${remainder}s` : `${remainder}s`
}

function formatDate(timestamp) {
  if (!timestamp) {
    return 'Date unavailable'
  }
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(timestamp))
}

function skillLabel(skill) {
  return skill === 'paced_breathing' ? 'Paced breathing' : '5-4-3-2-1 grounding'
}

async function loadHistory() {
  const user = accountSession.user.value
  if (!user) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  try {
    const sessionData = await sessionsApi.list(user.id)
    exerciseSessions.value = sessionData.sessions
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

watch(
  () => accountSession.user.value,
  (user) => {
    if (user) {
      loadHistory()
    }
  },
  { immediate: true },
)
</script>

<template>
  <main class="history-page" data-page="history">
    <header>
      <p class="eyebrow">Saved prototype activity</p>
      <h1>History</h1>
      <p>Review measured exercises stored for your account.</p>
    </header>

    <p v-if="isLoading" aria-live="polite">Loading saved activity…</p>
    <aside v-else-if="errorMessage" class="error-card" role="alert">
      <p>{{ errorMessage }}</p>
      <button type="button" @click="loadHistory">Retry history</button>
    </aside>

    <template v-else>
      <section aria-labelledby="exercise-heading">
        <h2 id="exercise-heading">Exercises</h2>
        <p v-if="exerciseSessions.length === 0">No saved exercises yet.</p>
        <ol v-else class="history-list">
          <li v-for="session in exerciseSessions" :key="session.id" class="history-card">
            <div>
              <strong>{{ skillLabel(session.skill) }}</strong>
              <span class="status-label">{{ session.status }}</span>
            </div>
            <p>Measured active time: {{ formatDuration(session.measured_active_duration_ms) }}</p>
            <p>Last step: {{ session.last_step || 'Not recorded' }}</p>
            <small>{{ formatDate(session.started_at) }}</small>
          </li>
        </ol>
      </section>

    </template>
  </main>
</template>

<style scoped>
.history-page {
  display: grid;
  width: min(100% - 2rem, 56rem);
  gap: 1.75rem;
  margin: 0 auto;
  padding: 2.5rem 0 3rem;
}

header,
section,
.history-list {
  display: grid;
  gap: 0.75rem;
}

h1 {
  color: var(--color-heading);
  font-size: clamp(2rem, 7vw, 3rem);
  font-weight: 750;
}

h2,
strong {
  font-weight: 750;
}

.eyebrow,
.status-label {
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.history-list {
  padding: 0;
  list-style: none;
}

.history-card {
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: var(--color-background-soft);
  box-shadow: var(--shadow-soft);
}

.history-card > div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.error-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid var(--color-danger);
  border-radius: 1rem;
  color: var(--color-danger-strong);
  background: var(--color-danger-soft);
}

button {
  min-height: 2.75rem;
  padding: 0.55rem 1rem;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  color: var(--color-on-primary);
  background: var(--color-primary);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

@media (max-width: 34rem) {
  .history-card > div,
  .error-card {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
