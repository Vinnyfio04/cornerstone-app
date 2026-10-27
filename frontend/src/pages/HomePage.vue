<script setup>
import BreathingCircle from '../components/BreathingCircle.vue'
import { createExercisePersistence } from '../session/exercisePersistence.js'
import { useDemoUserSession } from '../session/demoUser.js'

const demoUserSession = useDemoUserSession()
const breathingPersistence = createExercisePersistence({
  getUser: () => demoUserSession.user.value,
  plannedDurationMs: 60_000,
  skill: 'paced_breathing',
})

function startBreathingPersistence() {
  breathingPersistence.start()
}

function finishBreathingPersistence(result) {
  breathingPersistence.finish(result)
}
</script>

<template>
  <main class="home-page" data-page="home">
    <header class="home-introduction">
      <p class="eyebrow">Start here</p>
      <h1>Take one steady moment.</h1>
    </header>

    <BreathingCircle
      @exercise-started="startBreathingPersistence"
      @exercise-finished="finishBreathingPersistence"
    />

    <p
      v-if="['starting', 'saving'].includes(breathingPersistence.status.value)"
      class="persistence-note"
      aria-live="polite"
    >
      Saving breathing activity…
    </p>
    <p
      v-else-if="['error', 'unsaved'].includes(breathingPersistence.status.value)"
      class="persistence-note persistence-error"
      aria-live="polite"
    >
      This breathing result was not saved. The exercise remains available.
    </p>

    <section class="action-card grounding-card" aria-labelledby="grounding-title">
      <p class="action-number" aria-hidden="true">5 · 4 · 3 · 2 · 1</p>
      <div>
        <h2 id="grounding-title">Sensory grounding</h2>
        <p>Move through five clear prompts using what you can see, feel, hear, smell, and taste.</p>
      </div>
      <RouterLink class="action-link action-link-primary" to="/grounding">
        Start 5-4-3-2-1 grounding
      </RouterLink>
    </section>

    <section class="action-card chat-card" aria-labelledby="chat-title">
      <div>
        <h2 id="chat-title">Talk through what happened</h2>
        <p>Open the conversation page when writing feels more useful than another exercise.</p>
      </div>
      <RouterLink class="action-link action-link-secondary" to="/chat">Start a chat</RouterLink>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  display: grid;
  gap: 1.5rem;
  width: min(100% - 2rem, 44rem);
  margin: 0 auto;
  padding: 2.5rem 0 3rem;
}

.home-introduction {
  display: grid;
  gap: 0.5rem;
  text-align: center;
}

.home-introduction h1,
.action-card h2 {
  color: var(--color-heading);
  font-weight: 700;
  line-height: 1.2;
}

.home-introduction h1 {
  font-size: clamp(2rem, 7vw, 3rem);
}

.eyebrow {
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.action-card {
  display: grid;
  align-items: center;
  gap: 0.4rem 1rem;
  padding: 1rem 1.1rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: var(--color-background-soft);
  box-shadow: var(--shadow-soft);
}

.grounding-card {
  grid-template-columns: auto minmax(0, 1fr) auto;
  border-color: var(--color-primary);
  background: linear-gradient(135deg, var(--color-background-soft), var(--color-primary-soft));
}

.chat-card {
  grid-template-columns: minmax(0, 1fr) auto;
  border-color: var(--color-secondary);
  background: linear-gradient(135deg, var(--color-background-soft), var(--color-secondary-soft));
}

.action-number {
  color: var(--color-primary);
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.action-card h2 {
  font-size: 1.1rem;
}

.action-card p:not(.action-number) {
  color: var(--color-text-soft);
  font-size: 0.87rem;
  line-height: 1.45;
}

.action-link {
  display: inline-flex;
  min-height: 2.65rem;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  padding: 0.4rem 0.9rem;
  font-weight: 700;
  text-align: center;
  text-decoration: none;
}

.action-link-primary {
  color: var(--color-on-primary);
  background: var(--color-primary);
}

.action-link-secondary {
  border-color: var(--color-secondary-strong);
  color: var(--color-secondary-strong);
  background: var(--color-background-soft);
}

.action-link:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

.persistence-note {
  margin-top: -0.75rem;
  color: var(--color-warning);
  font-size: 0.85rem;
  text-align: center;
}

.persistence-error {
  color: var(--color-danger);
}

@media (max-width: 38rem) {
  .grounding-card,
  .chat-card {
    grid-template-columns: 1fr;
  }

  .action-link {
    justify-self: start;
  }
}
</style>
