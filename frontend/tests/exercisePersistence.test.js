import assert from 'node:assert/strict'
import test from 'node:test'

import { createExercisePersistence } from '../src/session/exercisePersistence.js'

test('starts and finishes one persisted exercise session', async () => {
  const calls = []
  const persistence = createExercisePersistence({
    getUser: () => ({ id: 8 }),
    plannedDurationMs: 60_000,
    skill: 'paced_breathing',
    requests: {
      async start(userId, skill, plannedDurationMs) {
        calls.push(['start', userId, skill, plannedDurationMs])
        return { id: 31, status: 'active' }
      },
      async finish(sessionId, result) {
        calls.push(['finish', sessionId, result])
        return { id: sessionId, ...result }
      },
    },
  })

  await persistence.start()
  const saved = await persistence.finish({
    status: 'exited',
    measuredActiveDurationMs: 18_420,
    lastStep: 'inhale_cycle_2',
  })

  assert.equal(saved.id, 31)
  assert.equal(persistence.status.value, 'saved')
  assert.deepEqual(calls, [
    ['start', 8, 'paced_breathing', 60_000],
    [
      'finish',
      31,
      {
        status: 'exited',
        measuredActiveDurationMs: 18_420,
        lastStep: 'inhale_cycle_2',
      },
    ],
  ])
})

test('does not persist an exercise without a signed-in account', async () => {
  const persistence = createExercisePersistence({
    getUser: () => null,
    skill: 'sensory_grounding',
    requests: {
      async start() {
        throw new Error('must not be called')
      },
    },
  })

  assert.equal(await persistence.start(), null)
  assert.equal(
    await persistence.finish({ status: 'completed', measuredActiveDurationMs: 1, lastStep: 'taste_1' }),
    null,
  )
  assert.equal(persistence.status.value, 'unsaved')
})
