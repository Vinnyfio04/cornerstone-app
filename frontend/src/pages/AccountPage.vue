<script setup>
import { ref, watch } from 'vue'

import { useDemoUserSession } from '../session/demoUser.js'

const demoUserSession = useDemoUserSession()
const displayName = ref('')
const isSaving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

async function saveAccount() {
  const trimmedName = displayName.value.trim()
  if (!trimmedName || isSaving.value) {
    return
  }

  isSaving.value = true
  successMessage.value = ''
  errorMessage.value = ''
  try {
    await demoUserSession.updateDisplayName(trimmedName)
    successMessage.value = 'Fictional demo account saved.'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isSaving.value = false
  }
}

function retryAccount() {
  demoUserSession.initialize({ force: true }).catch(() => {})
}

watch(
  () => demoUserSession.user.value,
  (user) => {
    displayName.value = user?.display_name ?? ''
  },
  { immediate: true },
)
</script>

<template>
  <main class="account-page" data-page="account">
    <header>
      <p class="eyebrow">Prototype-only identity</p>
      <h1>Account</h1>
      <p>
        This phase uses one fictional local demo user to connect browser activity to SQLite. It
        does not provide registration, login, or authentication.
      </p>
    </header>

    <p v-if="demoUserSession.isLoading.value" aria-live="polite">Loading account…</p>
    <aside v-else-if="!demoUserSession.user.value" class="error-card" role="alert">
      <p>The fictional account could not be loaded.</p>
      <button type="button" @click="retryAccount">Retry account</button>
    </aside>

    <form v-else class="account-form" @submit.prevent="saveAccount">
      <label for="display-name">Display name</label>
      <input
        id="display-name"
        v-model="displayName"
        maxlength="80"
        required
        autocomplete="off"
      />
      <p class="account-id">SQLite user identifier: {{ demoUserSession.user.value.id }}</p>
      <button type="submit" :disabled="!displayName.trim() || isSaving">
        {{ isSaving ? 'Saving…' : 'Save account' }}
      </button>
    </form>

    <p v-if="successMessage" class="success-message" role="status">{{ successMessage }}</p>
    <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
  </main>
</template>

<style scoped>
.account-page {
  display: grid;
  width: min(100% - 2rem, 40rem);
  align-content: start;
  gap: 1.25rem;
  margin: 0 auto;
  padding: 2.5rem 0 3rem;
}

header,
.account-form {
  display: grid;
  gap: 0.65rem;
}

h1 {
  color: var(--color-heading);
  font-size: clamp(2rem, 7vw, 3rem);
  font-weight: 750;
}

.eyebrow {
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 750;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.account-form {
  padding: 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: var(--color-background-soft);
  box-shadow: var(--shadow-soft);
}

label {
  font-weight: 700;
}

input {
  min-height: 3rem;
  padding: 0.65rem 0.8rem;
  border: 2px solid var(--color-border-hover);
  border-radius: 0.75rem;
  color: var(--color-text);
  background: var(--color-background-soft);
  font: inherit;
}

button {
  justify-self: start;
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

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

input:focus-visible,
button:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

.account-id {
  color: var(--color-text-soft);
  font-size: 0.85rem;
}

.success-message,
.error-message,
.error-card {
  padding: 0.85rem 1rem;
  border-radius: 0.75rem;
}

.success-message {
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
}

.error-message,
.error-card {
  color: var(--color-danger-strong);
  background: var(--color-danger-soft);
}

.error-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border: 2px solid var(--color-danger);
}
</style>
