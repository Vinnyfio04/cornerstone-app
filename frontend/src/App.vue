<script setup>
import { RouterView } from 'vue-router'

import AppNavigation from './components/AppNavigation.vue'
import PersistentSupportLink from './components/PersistentSupportLink.vue'
import { useDemoUserSession } from './session/demoUser.js'

const demoUserSession = useDemoUserSession()

function retryDemoUser() {
  demoUserSession.initialize({ force: true }).catch(() => {})
}
</script>

<template>
  <div class="app-shell">
    <header class="application-header">
      <RouterLink class="brand-link" to="/">Cornerstone</RouterLink>
      <p>Grounding support coursework prototype</p>
      <PersistentSupportLink />
    </header>

    <AppNavigation />

    <aside
      v-if="demoUserSession.isLoading.value || demoUserSession.error.value"
      class="connection-status"
      :class="{ 'connection-error': demoUserSession.error.value }"
      aria-live="polite"
    >
      <p v-if="demoUserSession.isLoading.value">Connecting the fictional demo account…</p>
      <template v-else>
        <p>The server is unavailable. Exercises still work, but this activity cannot be saved yet.</p>
        <button type="button" @click="retryDemoUser">Retry connection</button>
      </template>
    </aside>

    <RouterView />

    <footer class="application-footer">
      <p>This prototype is not a substitute for emergency or professional care.</p>
    </footer>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  padding-bottom: calc(5.25rem + env(safe-area-inset-bottom));
}

.application-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1.5rem;
  padding: 1rem max(1rem, calc((100% - 70rem) / 2));
  border-bottom: 1px solid var(--color-border);
  background: var(--color-background);
}

.brand-link {
  color: var(--color-primary-strong);
  font-size: 1.35rem;
  font-weight: 800;
  text-decoration: none;
}

.application-header p {
  flex: 1;
  font-size: 0.85rem;
}

.application-footer {
  margin-top: auto;
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.8rem;
  text-align: center;
  color: var(--color-text-soft);
  background: rgba(255, 250, 242, 0.72);
}

.connection-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.7rem 1rem;
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
  text-align: center;
}

.connection-error {
  color: var(--color-danger-strong);
  background: var(--color-danger-soft);
}

.connection-status button {
  min-height: 2.25rem;
  padding: 0.35rem 0.8rem;
  border: 2px solid currentcolor;
  border-radius: 999px;
  color: inherit;
  background: var(--color-background-soft);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

@media (max-width: 40rem) {
  .application-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .connection-status {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
