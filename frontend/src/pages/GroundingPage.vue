<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import GroundingPrompt from '../components/GroundingPrompt.vue'
import { useDemoUserSession } from '../session/demoUser.js'
import { createExercisePersistence } from '../session/exercisePersistence.js'
import {
  GROUNDING_STEPS,
  buildGroundingResult,
  formatGroundingDuration,
} from '../utils/groundingSequence.js'

const currentStepIndex = ref(0)
const exerciseStatus = ref('active')
const measuredDurationMs = ref(0)
const result = ref(null)
const demoUserSession = useDemoUserSession()
const groundingPersistence = createExercisePersistence({
  getUser: () => demoUserSession.user.value,
  skill: 'sensory_grounding',
})

let startedAt = null
let timerId = null

const currentStep = computed(() => GROUNDING_STEPS[currentStepIndex.value])
const currentStepNumber = computed(() => currentStepIndex.value + 1)
const isFirstStep = computed(() => currentStepIndex.value === 0)
const isLastStep = computed(() => currentStepIndex.value === GROUNDING_STEPS.length - 1)
const measuredDuration = computed(() => formatGroundingDuration(measuredDurationMs.value))
const outcomeHeading = computed(() =>
  exerciseStatus.value === 'completed' ? 'Grounding sequence complete' : 'You left the exercise',
)

function clearTimer() {
  if (timerId !== null) {
    window.clearInterval(timerId)
    timerId = null
  }
}

function updateMeasuredDuration() {
  if (exerciseStatus.value === 'active' && startedAt !== null) {
    measuredDurationMs.value = window.performance.now() - startedAt
  }
}

function startTiming() {
  clearTimer()
  measuredDurationMs.value = 0
  startedAt = window.performance.now()
  timerId = window.setInterval(updateMeasuredDuration, 100)
}

function finishExercise(status) {
  if (exerciseStatus.value !== 'active') {
    return
  }

  updateMeasuredDuration()
  clearTimer()
  result.value = buildGroundingResult(status, currentStepIndex.value, measuredDurationMs.value)
  measuredDurationMs.value = result.value.measuredActiveDurationMs
  exerciseStatus.value = status
  startedAt = null
  groundingPersistence.finish(result.value)
}

function goBack() {
  if (!isFirstStep.value && exerciseStatus.value === 'active') {
    currentStepIndex.value -= 1
  }
}

function goForward() {
  if (exerciseStatus.value !== 'active') {
    return
  }

  if (isLastStep.value) {
    finishExercise('completed')
    return
  }

  currentStepIndex.value += 1
}

function leaveExercise() {
  finishExercise('exited')
}

function restartExercise() {
  currentStepIndex.value = 0
  exerciseStatus.value = 'active'
  result.value = null
  groundingPersistence.reset()
  groundingPersistence.start()
  startTiming()
}

onMounted(() => {
  startTiming()
  groundingPersistence.start()
})

watch(
  () => demoUserSession.user.value,
  (user) => {
    if (
      user &&
      exerciseStatus.value === 'active' &&
      ['idle', 'unsaved'].includes(groundingPersistence.status.value)
    ) {
      groundingPersistence.start()
    }
  },
)

onBeforeUnmount(() => {
  if (exerciseStatus.value === 'active') {
    finishExercise('exited')
  }

  clearTimer()
})
</script>

<template>
  <main class="grounding-page" data-page="grounding">
    <header class="grounding-heading">
      <p class="eyebrow">Sensory grounding</p>
      <h1>5-4-3-2-1</h1>
      <p>Move at your own pace. Simply notice each item before continuing.</p>
    </header>

    <template v-if="exerciseStatus === 'active'">
      <div class="progress-group">
        <label for="grounding-progress">
          Step {{ currentStepNumber }} of {{ GROUNDING_STEPS.length }} · {{ measuredDuration }}
        </label>
        <progress
          id="grounding-progress"
          :value="currentStepNumber"
          :max="GROUNDING_STEPS.length"
        />
      </div>

      <GroundingPrompt
        :key="currentStep.id"
        :step="currentStep"
        :step-number="currentStepNumber"
        :total-steps="GROUNDING_STEPS.length"
      />

      <div class="exercise-controls" aria-label="Grounding exercise controls">
        <button type="button" :disabled="isFirstStep" @click="goBack">Back</button>
        <button class="leave-button" type="button" @click="leaveExercise">Leave exercise</button>
        <button class="next-button" type="button" @click="goForward">
          {{ isLastStep ? 'Finish' : 'Next' }}
        </button>
      </div>
    </template>

    <p
      v-if="['starting', 'saving'].includes(groundingPersistence.status.value)"
      class="persistence-note"
      aria-live="polite"
    >
      Saving grounding activity…
    </p>
    <p
      v-else-if="groundingPersistence.status.value === 'saved'"
      class="persistence-note persistence-saved"
      aria-live="polite"
    >
      Grounding activity saved to this fictional demo account.
    </p>
    <p
      v-else-if="['error', 'unsaved'].includes(groundingPersistence.status.value)"
      class="persistence-note persistence-error"
      aria-live="polite"
    >
      This grounding result was not saved. The exercise remains available.
    </p>

    <section v-if="exerciseStatus !== 'active'" class="outcome-card" aria-live="polite">
      <p class="outcome-status">{{ exerciseStatus }}</p>
      <h2>{{ outcomeHeading }}</h2>
      <p>
        Measured duration: <strong>{{ measuredDuration }}</strong>
      </p>
      <p>Last step: {{ currentStep.title }}</p>
      <div class="outcome-actions">
        <button type="button" @click="restartExercise">Start again</button>
        <RouterLink to="/">Return home</RouterLink>
      </div>
    </section>
  </main>
</template>

<style scoped>
.grounding-page {
  display: grid;
  width: min(100% - 2rem, 46rem);
  gap: 1.5rem;
  margin: 0 auto;
  padding: 2.5rem 0 3rem;
}

.grounding-heading {
  display: grid;
  gap: 0.4rem;
  text-align: center;
}

.grounding-heading h1,
.outcome-card h2 {
  color: var(--color-heading);
  font-weight: 750;
  line-height: 1.2;
}

.grounding-heading h1 {
  font-size: clamp(2.3rem, 10vw, 4rem);
}

.eyebrow,
.outcome-status {
  color: var(--color-primary);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.progress-group {
  display: grid;
  gap: 0.4rem;
}

.progress-group label {
  font-size: 0.85rem;
  font-weight: 650;
}

progress {
  width: 100%;
  height: 0.8rem;
  accent-color: var(--color-primary);
}

.exercise-controls,
.outcome-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.persistence-note {
  color: var(--color-warning);
  font-size: 0.85rem;
  text-align: center;
}

.persistence-saved {
  color: var(--color-primary);
}

.persistence-error {
  color: var(--color-danger);
}

button,
.outcome-actions a {
  display: inline-flex;
  min-height: 3rem;
  align-items: center;
  justify-content: center;
  padding: 0.6rem 1rem;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  color: var(--color-primary-strong);
  background: var(--color-background-soft);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
  text-align: center;
  text-decoration: none;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.leave-button {
  border-color: var(--color-danger);
  color: var(--color-danger);
  background: var(--color-danger-soft);
}

.next-button,
.outcome-actions a {
  color: var(--color-on-primary);
  background: var(--color-primary);
}

button:focus-visible,
.outcome-actions a:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

.outcome-card {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: clamp(1.5rem, 6vw, 3rem);
  border: 2px solid var(--color-primary);
  border-radius: 1.5rem;
  background: linear-gradient(145deg, var(--color-primary-soft), var(--color-background-soft));
  box-shadow: var(--shadow-raised);
  text-align: center;
}

.outcome-actions {
  width: min(100%, 28rem);
  grid-template-columns: repeat(2, 1fr);
}

@media (max-width: 34rem) {
  .exercise-controls {
    grid-template-columns: repeat(2, 1fr);
  }

  .leave-button {
    grid-column: 1 / -1;
    grid-row: 2;
  }

  .outcome-actions {
    grid-template-columns: 1fr;
  }
}
</style>
