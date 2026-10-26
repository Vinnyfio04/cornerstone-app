<script setup>
defineProps({
  step: {
    type: Object,
    required: true,
  },
  stepNumber: {
    type: Number,
    required: true,
  },
  totalSteps: {
    type: Number,
    required: true,
  },
})
</script>

<template>
  <article class="grounding-prompt" :aria-labelledby="`grounding-step-${stepNumber}`">
    <p class="step-position">Step {{ stepNumber }} of {{ totalSteps }}</p>
    <p class="sense-count" aria-hidden="true">{{ step.count }}</p>
    <h2 :id="`grounding-step-${stepNumber}`">{{ step.title }}</h2>
    <p class="step-instruction">{{ step.prompt }}</p>
    <p class="no-input-note">You do not need to type or share your answers.</p>
  </article>
</template>

<style scoped>
.grounding-prompt {
  display: grid;
  min-height: 23rem;
  align-content: center;
  justify-items: center;
  gap: 1rem;
  padding: clamp(1.5rem, 6vw, 3rem);
  border: 2px solid var(--color-primary);
  border-radius: 1.5rem;
  color: var(--color-primary-strong);
  background: linear-gradient(145deg, var(--color-primary-soft), var(--color-background-soft));
  text-align: center;
  box-shadow: var(--shadow-raised);
}

.step-position {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.sense-count {
  display: grid;
  width: 6rem;
  aspect-ratio: 1;
  place-items: center;
  border-radius: 50%;
  color: var(--color-on-primary);
  background: var(--color-primary);
  font-size: 3rem;
  font-weight: 800;
  line-height: 1;
}

h2 {
  font-size: clamp(1.6rem, 6vw, 2.35rem);
  font-weight: 750;
  line-height: 1.2;
}

.step-instruction {
  max-width: 32rem;
  font-size: 1.05rem;
}

.no-input-note {
  font-size: 0.85rem;
}
</style>
