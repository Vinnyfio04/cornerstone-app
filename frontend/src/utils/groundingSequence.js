export const GROUNDING_STEPS = Object.freeze([
  Object.freeze({
    id: 'see_5',
    count: 5,
    sense: 'see',
    title: 'Notice five things you can see',
    prompt: 'Let your eyes move slowly. Notice five shapes, colors, objects, or points of light.',
  }),
  Object.freeze({
    id: 'feel_4',
    count: 4,
    sense: 'feel',
    title: 'Notice four things you can feel',
    prompt: 'Notice four physical sensations, such as your feet, clothing, chair, or the air.',
  }),
  Object.freeze({
    id: 'hear_3',
    count: 3,
    sense: 'hear',
    title: 'Notice three things you can hear',
    prompt: 'Listen for three sounds nearby or farther away. They can be quiet or ordinary.',
  }),
  Object.freeze({
    id: 'smell_2',
    count: 2,
    sense: 'smell',
    title: 'Notice two things you can smell',
    prompt: 'Notice two scents in the space, on your clothing, or simply in the air around you.',
  }),
  Object.freeze({
    id: 'taste_1',
    count: 1,
    sense: 'taste',
    title: 'Notice one thing you can taste',
    prompt: 'Notice one taste that is already present. There is no need to find or eat anything.',
  }),
])

export function getGroundingStep(stepIndex) {
  if (!Number.isInteger(stepIndex) || stepIndex < 0 || stepIndex >= GROUNDING_STEPS.length) {
    return null
  }

  return GROUNDING_STEPS[stepIndex]
}

export function buildGroundingResult(status, stepIndex, measuredDurationMs) {
  if (status !== 'completed' && status !== 'exited') {
    throw new TypeError('Grounding status must be completed or exited.')
  }

  const step = getGroundingStep(stepIndex)

  if (step === null) {
    throw new RangeError('Grounding step index is outside the sequence.')
  }

  const safeDuration = Number.isFinite(measuredDurationMs) ? Math.max(0, measuredDurationMs) : 0

  return Object.freeze({
    lastStep: step.id,
    measuredActiveDurationMs: Math.round(safeDuration),
    status,
  })
}

export function formatGroundingDuration(measuredDurationMs) {
  return `${(measuredDurationMs / 1_000).toFixed(1)} seconds`
}
