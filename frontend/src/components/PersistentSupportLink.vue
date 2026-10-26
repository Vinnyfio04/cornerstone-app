<script setup>
import { announceSupportAction } from '../voice/voiceLifecycle.js'

function handleSupportAction() {
  announceSupportAction()
}
</script>

<template>
  <RouterLink class="support-link" to="/support" @click="handleSupportAction">
    Crisis support information
  </RouterLink>
</template>

<style scoped>
.support-link {
  display: inline-flex;
  min-height: 2.75rem;
  align-items: center;
  padding: 0.5rem 0.9rem;
  border: 2px solid var(--color-danger);
  border-radius: 999px;
  color: var(--color-danger);
  background: var(--color-danger-soft);
  font-weight: 700;
  text-decoration: none;
}

.support-link:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 2px;
}

</style>
