import assert from 'node:assert/strict'
import test from 'node:test'

import {
  BREATHING_TOTAL_DURATION_MS,
  formatMeasuredDuration,
  getBreathingSnapshot,
} from '../src/utils/breathingTimeline.js'

test('uses a four-second inhale and six-second exhale for each cycle', () => {
  assert.deepEqual(getBreathingSnapshot(0).phase, 'inhale')
  assert.deepEqual(getBreathingSnapshot(3_999).phase, 'inhale')
  assert.deepEqual(getBreathingSnapshot(4_000).phase, 'exhale')
  assert.deepEqual(getBreathingSnapshot(9_999).phase, 'exhale')
  assert.deepEqual(getBreathingSnapshot(10_000).phase, 'inhale')
  assert.deepEqual(getBreathingSnapshot(10_000).cycle, 2)
})

test('resets ring progress for each inhale and exhale phase', () => {
  assert.equal(getBreathingSnapshot(0).phaseProgressPercent, 0)
  assert.equal(getBreathingSnapshot(2_000).phaseProgressPercent, 50)
  assert.ok(getBreathingSnapshot(3_999).phaseProgressPercent > 99)

  assert.equal(getBreathingSnapshot(4_000).phaseProgressPercent, 0)
  assert.equal(getBreathingSnapshot(7_000).phaseProgressPercent, 50)
  assert.ok(getBreathingSnapshot(9_999).phaseProgressPercent > 99)

  assert.equal(getBreathingSnapshot(10_000).phaseProgressPercent, 0)
})

test('completes at six cycles and clamps longer measurements', () => {
  const justBeforeCompletion = getBreathingSnapshot(BREATHING_TOTAL_DURATION_MS - 1)
  const completed = getBreathingSnapshot(BREATHING_TOTAL_DURATION_MS)
  const overrun = getBreathingSnapshot(BREATHING_TOTAL_DURATION_MS + 5_000)

  assert.equal(justBeforeCompletion.completed, false)
  assert.equal(justBeforeCompletion.cycle, 6)
  assert.equal(completed.completed, true)
  assert.equal(completed.phase, 'complete')
  assert.equal(completed.phaseProgressPercent, 100)
  assert.equal(completed.progressPercent, 100)
  assert.equal(overrun.measuredActiveDurationMs, BREATHING_TOTAL_DURATION_MS)
})

test('normalizes invalid time and formats measured duration', () => {
  assert.equal(getBreathingSnapshot(-50).measuredActiveDurationMs, 0)
  assert.equal(getBreathingSnapshot(Number.NaN).measuredActiveDurationMs, 0)
  assert.equal(formatMeasuredDuration(18_420), '18.4 seconds')
})
