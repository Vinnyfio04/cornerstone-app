<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import {
  BREATHING_CYCLE_DURATION_MS,
  BREATHING_CYCLE_COUNT,
  EXHALE_DURATION_MS,
  formatMeasuredDuration,
  getBreathingSnapshot,
  INHALE_DURATION_MS,
} from '../utils/breathingTimeline.js'

const emit = defineEmits(['exerciseStarted', 'exerciseFinished'])

const exerciseStatus = ref('idle')
const endReason = ref(null)
const snapshot = ref(getBreathingSnapshot(0))

let animationFrameId = null
let startedAt = null

const MINIMUM_CIRCLE_SCALE = 0.74
const MAXIMUM_CIRCLE_SCALE = 1.08

const isActive = computed(() => exerciseStatus.value === 'active')
const measuredDuration = computed(() =>
  formatMeasuredDuration(snapshot.value.measuredActiveDurationMs),
)
const circleLabel = computed(() => {
  if (exerciseStatus.value === 'completed') {
    return 'Sequence complete'
  }

  if (!isActive.value) {
    return 'Hold with thumb'
  }

  return snapshot.value.phase === 'inhale' ? 'Breathe in' : 'Breathe out'
})
const statusMessage = computed(() => {
  if (exerciseStatus.value === 'completed') {
    return `Six cycles complete in ${measuredDuration.value}. Release when you are ready.`
  }

  if (exerciseStatus.value === 'exited') {
    if (endReason.value === 'visibility') {
      return `Breathing stopped when the page left view at ${measuredDuration.value}.`
    }

    return `Breathing stopped at ${measuredDuration.value}.`
  }

  if (isActive.value) {
    const phase = snapshot.value.phase === 'inhale' ? 'Breathe in' : 'Breathe out'
    return `${phase}. Cycle ${snapshot.value.cycle} of ${BREATHING_CYCLE_COUNT}. ${measuredDuration.value} active.`
  }

  return 'Press and hold the circle, or use the keyboard start and stop control.'
})
const announcementMessage = computed(() => {
  if (exerciseStatus.value === 'completed') {
    return `Six breathing cycles complete in ${measuredDuration.value}.`
  }

  if (exerciseStatus.value === 'exited') {
    return `Breathing stopped at ${measuredDuration.value}.`
  }

  if (isActive.value) {
    const phase = snapshot.value.phase === 'inhale' ? 'Breathe in' : 'Breathe out'
    return `${phase}. Cycle ${snapshot.value.cycle} of ${BREATHING_CYCLE_COUNT}.`
  }

  return 'Breathing control ready.'
})
const progressStyle = computed(() => {
  let scale = MINIMUM_CIRCLE_SCALE

  if (isActive.value) {
    const cycleElapsedMs =
      snapshot.value.measuredActiveDurationMs % BREATHING_CYCLE_DURATION_MS

    if (snapshot.value.phase === 'inhale') {
      const phaseProgress = cycleElapsedMs / INHALE_DURATION_MS
      scale += (MAXIMUM_CIRCLE_SCALE - MINIMUM_CIRCLE_SCALE) * phaseProgress
    } else if (snapshot.value.phase === 'exhale') {
      const phaseProgress = (cycleElapsedMs - INHALE_DURATION_MS) / EXHALE_DURATION_MS
      scale = MAXIMUM_CIRCLE_SCALE -
        (MAXIMUM_CIRCLE_SCALE - MINIMUM_CIRCLE_SCALE) * phaseProgress
    }
  }

  return {
    '--breathing-scale': scale.toFixed(4),
    '--exercise-progress': `${snapshot.value.phaseProgressPercent}%`,
  }
})

function cancelAnimationFrameUpdate() {
  if (animationFrameId !== null) {
    window.cancelAnimationFrame(animationFrameId)
    animationFrameId = null
  }
}

function completeExercise() {
  cancelAnimationFrameUpdate()
  exerciseStatus.value = 'completed'
  endReason.value = 'completed'
  startedAt = null
  emit('exerciseFinished', {
    status: 'completed',
    measuredActiveDurationMs: Math.round(snapshot.value.measuredActiveDurationMs),
    lastStep: 'exhale_cycle_6',
  })
}

function updateExercise(currentTime) {
  if (!isActive.value || startedAt === null) {
    return
  }

  snapshot.value = getBreathingSnapshot(currentTime - startedAt)

  if (snapshot.value.completed) {
    completeExercise()
    return
  }

  animationFrameId = window.requestAnimationFrame(updateExercise)
}

function startExercise() {
  if (isActive.value) {
    return
  }

  cancelAnimationFrameUpdate()
  exerciseStatus.value = 'active'
  endReason.value = null
  snapshot.value = getBreathingSnapshot(0)
  startedAt = window.performance.now()
  emit('exerciseStarted')
  animationFrameId = window.requestAnimationFrame(updateExercise)
}

function stopExercise(reason = 'release') {
  if (!isActive.value || startedAt === null) {
    return
  }

  snapshot.value = getBreathingSnapshot(window.performance.now() - startedAt)
  cancelAnimationFrameUpdate()

  if (snapshot.value.completed) {
    completeExercise()
    return
  }

  exerciseStatus.value = 'exited'
  endReason.value = reason
  startedAt = null
  emit('exerciseFinished', {
    status: 'exited',
    measuredActiveDurationMs: Math.round(snapshot.value.measuredActiveDurationMs),
    lastStep: `${snapshot.value.phase}_cycle_${snapshot.value.cycle}`,
  })
}

function handlePointerDown(event) {
  if (event.pointerType === 'mouse' && event.button !== 0) {
    return
  }

  event.preventDefault()
  event.currentTarget.setPointerCapture?.(event.pointerId)
  startExercise()
}

function handlePointerEnd(event) {
  stopExercise('release')

  if (event.currentTarget.hasPointerCapture?.(event.pointerId)) {
    event.currentTarget.releasePointerCapture(event.pointerId)
  }
}

function handleVisibilityChange() {
  if (document.hidden) {
    stopExercise('visibility')
  }
}

onMounted(() => {
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onBeforeUnmount(() => {
  stopExercise('navigation')
  cancelAnimationFrameUpdate()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<template>
  <section class="breathing-control" aria-labelledby="breathing-title">
    <div class="breathing-heading">
      <p class="control-label">Breathing practice</p>
      <h2 id="breathing-title">Follow a gentle 4–6 pace</h2>
    </div>

    <button
      class="breathing-circle"
      :class="{
        'breathing-circle-active': isActive,
        'breathing-circle-inhale': isActive && snapshot.phase === 'inhale',
        'breathing-circle-exhale': isActive && snapshot.phase === 'exhale',
        'breathing-circle-hold': isActive && snapshot.phase === 'hold',
      }"
      :style="progressStyle"
      type="button"
      aria-describedby="breathing-status"
      @pointerdown="handlePointerDown"
      @pointerup="handlePointerEnd"
      @pointercancel="handlePointerEnd"
      @lostpointercapture="stopExercise('release')"
      @keydown.space.prevent="startExercise"
      @keyup.space.prevent="stopExercise('keyboard-hold')"
      @keydown.enter.prevent="startExercise"
      @keyup.enter.prevent="stopExercise('keyboard-hold')"
      @blur="stopExercise('blur')"
      @contextmenu.prevent
    >
      <span>{{ circleLabel }}</span>
      <small v-if="isActive">Cycle {{ snapshot.cycle }} of {{ BREATHING_CYCLE_COUNT }}</small>
      <small v-else>4 seconds in · 6 seconds out</small>
    </button>

    <p id="breathing-status" class="control-status">{{ statusMessage }}</p>
    <p class="visually-hidden" aria-live="polite">{{ announcementMessage }}</p>

    <aside v-if="exerciseStatus === 'completed'" class="grounding-follow-up" aria-live="polite">
      <p>Would another grounding approach help?</p>
      <RouterLink to="/grounding">Continue to 5-4-3-2-1 grounding</RouterLink>
    </aside>
  </section>
</template>

<style scoped>
.breathing-control {
  display: grid;
  justify-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 1.5rem;
  background: linear-gradient(145deg, var(--color-primary-soft), var(--color-secondary-soft));
  color: var(--color-primary-strong);
  box-shadow: var(--shadow-soft);
  text-align: center;
}

.breathing-heading {
  display: grid;
  gap: 0.25rem;
}

.breathing-heading h2 {
  font-size: 1.25rem;
  font-weight: 700;
}

.control-label {
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.breathing-circle {
  --breathing-scale: 0.74;
  --exercise-progress: 0%;
  position: relative;
  display: grid;
  width: min(68vw, 17rem);
  aspect-ratio: 1;
  place-content: center;
  gap: 0.5rem;
  border: 0;
  border-radius: 50%;
  color: var(--color-on-primary);
  background: radial-gradient(
    circle,
    rgba(79, 116, 94, 0.98) 0%,
    rgba(79, 116, 94, 0.94) 42%,
    rgba(79, 116, 94, 0.58) 62%,
    rgba(79, 116, 94, 0.18) 78%,
    rgba(79, 116, 94, 0.03) 91%,
    transparent 100%
  );
  box-shadow: 0 1rem 2.5rem rgba(54, 85, 69, 0.14);
  cursor: pointer;
  font: inherit;
  opacity: 1;
  touch-action: none;
  transform: scale(var(--breathing-scale));
  transition:
    box-shadow 300ms ease,
    filter 300ms ease;
  user-select: none;
  -webkit-user-select: none;
}

.breathing-circle::before {
  position: absolute;
  inset: -0.15rem;
  padding: 0.22rem;
  border-radius: inherit;
  background: conic-gradient(
    rgba(197, 162, 95, 0.72) var(--exercise-progress),
    rgba(255, 253, 248, 0.22) 0
  );
  content: '';
  pointer-events: none;
  -webkit-mask:
    linear-gradient(#000 0 0) content-box,
    linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

.breathing-circle-active {
  box-shadow: 0 1.25rem 3rem rgba(54, 85, 69, 0.28);
  filter: saturate(1.05);
}

.breathing-circle:hover,
.breathing-circle:active {
  transform: scale(var(--breathing-scale));
}

.breathing-circle-inhale {
  box-shadow: 0 1.4rem 3.5rem rgba(54, 85, 69, 0.24);
}

.breathing-circle-exhale {
  box-shadow: 0 0.75rem 2rem rgba(54, 85, 69, 0.12);
}

.breathing-circle-hold {
  transition: none;
}

.breathing-circle:focus-visible,
.grounding-follow-up a:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 4px;
}

.breathing-circle span {
  position: relative;
  z-index: 1;
  font-size: 1.35rem;
  font-weight: 700;
  text-shadow: 0 1px 5px rgba(40, 60, 51, 0.3);
}

.breathing-circle small {
  position: relative;
  z-index: 1;
  font-size: 0.82rem;
  text-shadow: 0 1px 4px rgba(40, 60, 51, 0.3);
}

.control-status {
  max-width: 28rem;
  min-height: 2.75rem;
  font-size: 0.85rem;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

.grounding-follow-up {
  display: grid;
  width: min(100%, 28rem);
  gap: 0.5rem;
  padding: 1rem;
  border: 2px solid var(--color-primary);
  border-radius: 1rem;
  background: var(--color-background-soft);
}

.grounding-follow-up p {
  font-weight: 700;
}

.grounding-follow-up a {
  color: var(--color-primary);
  font-weight: 700;
}

@media (prefers-reduced-motion: reduce) {
  .breathing-circle {
    transition: none;
  }

  .breathing-circle-inhale,
  .breathing-circle-exhale,
  .breathing-circle-hold {
    transition: none;
  }
}
</style>
