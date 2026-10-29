<script setup>
import { RouterView } from 'vue-router'

import AppNavigation from './components/AppNavigation.vue'
import PersistentSupportLink from './components/PersistentSupportLink.vue'
import { useAccountSession } from './session/accountSession.js'

const accountSession = useAccountSession()

function retryAccount() {
  accountSession.initialize({ force: true }).catch(() => {})
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
      v-if="accountSession.isLoading.value || accountSession.error.value"
      class="connection-status"
      :class="{ 'connection-error': accountSession.error.value }"
      aria-live="polite"
    >
      <p v-if="accountSession.isLoading.value">Checking your saved sign-in…</p>
      <template v-else>
        <p>The server is unavailable. Breathing and support information remain available.</p>
        <button type="button" @click="retryAccount">Retry connection</button>
      </template>
    </aside>

    <RouterView v-slot="{ Component, route }">
      <main
        v-if="route.meta.requiresAccount && accountSession.isLoading.value"
        class="account-required"
        aria-live="polite"
      >
        <p>Checking your saved sign-in…</p>
      </main>
      <main v-else-if="route.meta.requiresAccount && !accountSession.user.value" class="account-required">
        <p class="eyebrow">Sign in required</p>
        <h1>Save this activity to your account.</h1>
        <p>Breathing and crisis-support information remain available without signing in.</p>
        <RouterLink class="account-link" to="/account">Go to account</RouterLink>
      </main>
      <component :is="Component" v-else />
    </RouterView>

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

.account-required {
  display: grid;
  width: min(100% - 2rem, 40rem);
  gap: 1rem;
  margin: 0 auto;
  padding: 3rem 0;
}

.account-required h1 {
  color: var(--color-heading);
  font-size: clamp(2rem, 7vw, 3rem);
}

.account-required .eyebrow {
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 750;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.account-link {
  display: inline-flex;
  min-height: 2.75rem;
  width: fit-content;
  align-items: center;
  padding: 0.55rem 1rem;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  color: var(--color-on-primary);
  background: var(--color-primary);
  font-weight: 700;
  text-decoration: none;
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
