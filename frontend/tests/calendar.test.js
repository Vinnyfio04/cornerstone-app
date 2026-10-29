import assert from 'node:assert/strict'
import test from 'node:test'

import {
  buildMonthGrid,
  canCreateCheckIn,
  feelingCategory,
  formatDateKey,
  shiftMonth,
} from '../src/utils/calendar.js'

test('builds a Sunday-first calendar grid with stable local date keys', () => {
  const cells = buildMonthGrid(new Date(2026, 9, 1))
  const datedCells = cells.filter(Boolean)

  assert.equal(cells.length, 35)
  assert.equal(cells[0], null)
  assert.equal(cells[4].dateKey, '2026-10-01')
  assert.equal(datedCells.at(-1).dateKey, '2026-10-31')
  assert.equal(formatDateKey(new Date(2026, 0, 2)), '2026-01-02')
})

test('moves between months without carrying an invalid day', () => {
  assert.equal(formatDateKey(shiftMonth(new Date(2026, 0, 31), 1)), '2026-02-01')
  assert.equal(formatDateKey(shiftMonth(new Date(2026, 0, 31), -1)), '2025-12-01')
})

test('maps custom feelings to the other marker category', () => {
  assert.equal(feelingCategory('Happy'), 'happy')
  assert.equal(feelingCategory('overwhelmed'), 'other')
})

test('allows check-ins for today and past dates but not future dates', () => {
  assert.equal(canCreateCheckIn('2026-10-28', '2026-10-28'), true)
  assert.equal(canCreateCheckIn('2026-10-26', '2026-10-28'), true)
  assert.equal(canCreateCheckIn('2026-10-29', '2026-10-28'), false)
  assert.equal(canCreateCheckIn('', '2026-10-28'), false)
})
