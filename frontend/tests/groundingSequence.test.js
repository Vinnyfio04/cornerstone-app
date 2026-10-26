import assert from 'node:assert/strict'
import test from 'node:test'

import {
  GROUNDING_STEPS,
  buildGroundingResult,
  formatGroundingDuration,
  getGroundingStep,
} from '../src/utils/groundingSequence.js'

test('keeps the sensory grounding sequence in 5-4-3-2-1 order', () => {
  assert.deepEqual(
    GROUNDING_STEPS.map(({ count, sense }) => [count, sense]),
    [
      [5, 'see'],
      [4, 'feel'],
      [3, 'hear'],
      [2, 'smell'],
      [1, 'taste'],
    ],
  )
})

test('returns only valid grounding steps', () => {
  assert.equal(getGroundingStep(0)?.id, 'see_5')
  assert.equal(getGroundingStep(4)?.id, 'taste_1')
  assert.equal(getGroundingStep(-1), null)
  assert.equal(getGroundingStep(5), null)
  assert.equal(getGroundingStep(1.5), null)
})

test('builds completed and exited results with the visible last step', () => {
  assert.deepEqual(buildGroundingResult('exited', 2, 18_420), {
    lastStep: 'hear_3',
    measuredActiveDurationMs: 18_420,
    status: 'exited',
  })
  assert.deepEqual(buildGroundingResult('completed', 4, 42_230.6), {
    lastStep: 'taste_1',
    measuredActiveDurationMs: 42_231,
    status: 'completed',
  })
  assert.equal(formatGroundingDuration(18_420), '18.4 seconds')
})

test('rejects illegal grounding results', () => {
  assert.throws(() => buildGroundingResult('active', 0, 100), TypeError)
  assert.throws(() => buildGroundingResult('exited', 8, 100), RangeError)
})
