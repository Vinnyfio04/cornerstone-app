export const INHALE_DURATION_MS = 4_000
export const EXHALE_DURATION_MS = 6_000
export const BREATHING_CYCLE_DURATION_MS = INHALE_DURATION_MS + EXHALE_DURATION_MS
export const BREATHING_CYCLE_COUNT = 6
export const BREATHING_TOTAL_DURATION_MS = BREATHING_CYCLE_DURATION_MS * BREATHING_CYCLE_COUNT

export function getBreathingSnapshot(elapsedMs) {
  const safeElapsedMs = Number.isFinite(elapsedMs) ? Math.max(0, elapsedMs) : 0
  const measuredActiveDurationMs = Math.min(safeElapsedMs, BREATHING_TOTAL_DURATION_MS)
  const completed = measuredActiveDurationMs >= BREATHING_TOTAL_DURATION_MS

  if (completed) {
    return {
      completed: true,
      cycle: BREATHING_CYCLE_COUNT,
      measuredActiveDurationMs,
      phase: 'complete',
      phaseProgressPercent: 100,
      progressPercent: 100,
    }
  }

  const cycleElapsedMs = measuredActiveDurationMs % BREATHING_CYCLE_DURATION_MS
  const phase = cycleElapsedMs < INHALE_DURATION_MS ? 'inhale' : 'exhale'
  const phaseElapsedMs =
    phase === 'inhale' ? cycleElapsedMs : cycleElapsedMs - INHALE_DURATION_MS
  const phaseDurationMs = phase === 'inhale' ? INHALE_DURATION_MS : EXHALE_DURATION_MS

  return {
    completed: false,
    cycle: Math.floor(measuredActiveDurationMs / BREATHING_CYCLE_DURATION_MS) + 1,
    measuredActiveDurationMs,
    phase,
    phaseProgressPercent: (phaseElapsedMs / phaseDurationMs) * 100,
    progressPercent: (measuredActiveDurationMs / BREATHING_TOTAL_DURATION_MS) * 100,
  }
}

export function formatMeasuredDuration(measuredActiveDurationMs) {
  return `${(measuredActiveDurationMs / 1_000).toFixed(1)} seconds`
}
