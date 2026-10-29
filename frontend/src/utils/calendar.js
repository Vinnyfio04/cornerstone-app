export const STANDARD_FEELINGS = ['happy', 'sad', 'stressed', 'scared']

export const FEELING_COLORS = Object.freeze({
  happy: '#d2a13f',
  sad: '#6f91aa',
  stressed: '#b06d4d',
  scared: '#86668f',
  other: '#66836e',
})

export function formatDateKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function buildMonthGrid(monthDate) {
  const year = monthDate.getFullYear()
  const month = monthDate.getMonth()
  const firstWeekday = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells = Array.from({ length: firstWeekday }, () => null)

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(year, month, day)
    cells.push({ day, dateKey: formatDateKey(date) })
  }
  while (cells.length % 7 !== 0) {
    cells.push(null)
  }
  return cells
}

export function shiftMonth(monthDate, offset) {
  return new Date(monthDate.getFullYear(), monthDate.getMonth() + offset, 1)
}

export function feelingCategory(feeling) {
  const normalized = feeling?.trim().toLowerCase()
  return STANDARD_FEELINGS.includes(normalized) ? normalized : 'other'
}

export function canCreateCheckIn(dateKey, todayKey) {
  return Boolean(dateKey) && dateKey <= todayKey
}
