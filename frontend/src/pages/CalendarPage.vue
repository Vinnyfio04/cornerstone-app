<script setup>
import { computed, ref, watch } from 'vue'

import { checkInsApi } from '../api/checkIns.js'
import { useAccountSession } from '../session/accountSession.js'
import {
  buildMonthGrid,
  canCreateCheckIn,
  FEELING_COLORS,
  feelingCategory,
  formatDateKey,
  shiftMonth,
} from '../utils/calendar.js'

const accountSession = useAccountSession()
const today = new Date()
const todayKey = formatDateKey(today)
const visibleMonth = ref(new Date(today.getFullYear(), today.getMonth(), 1))
const selectedDate = ref(todayKey)
const checkIns = ref([])
const selectedFeeling = ref('')
const otherFeeling = ref('')
const customColor = ref(FEELING_COLORS.other)
const description = ref('')
const isLoading = ref(false)
const isSaving = ref(false)
const isEditing = ref(false)
const errorMessage = ref('')
const confirmationMessage = ref('')

const feelingOptions = [
  { value: 'happy', label: 'Happy', symbol: '☀' },
  { value: 'sad', label: 'Sad', symbol: '◒' },
  { value: 'stressed', label: 'Stressed', symbol: '≋' },
  { value: 'scared', label: 'Scared', symbol: '◇' },
]
const customColorOptions = [
  '#66836e',
  '#4f7f8f',
  '#496db2',
  '#86668f',
  '#b45f74',
  '#c66f42',
  '#d2a13f',
  '#7b8f48',
]
const monthOptions = Array.from({ length: 12 }, (_, monthIndex) => ({
  value: monthIndex,
  label: new Intl.DateTimeFormat(undefined, { month: 'long' }).format(
    new Date(2026, monthIndex, 1),
  ),
}))

const monthCells = computed(() => buildMonthGrid(visibleMonth.value))
const yearOptions = computed(() => {
  const visibleYear = visibleMonth.value.getFullYear()
  const startYear = Math.min(today.getFullYear() - 25, visibleYear)
  const endYear = Math.max(today.getFullYear() + 5, visibleYear)
  return Array.from({ length: endYear - startYear + 1 }, (_, index) => startYear + index)
})
const checkInsByDate = computed(
  () => new Map(checkIns.value.map((checkIn) => [checkIn.check_in_date, checkIn])),
)
const selectedCheckIn = computed(() => checkInsByDate.value.get(selectedDate.value) ?? null)
const selectedDateLabel = computed(() => formatDisplayDate(selectedDate.value))
const canCreateSelectedDate = computed(
  () =>
    canCreateCheckIn(selectedDate.value, todayKey) &&
    selectedCheckIn.value === null,
)
const formHeading = computed(() =>
  selectedDate.value === todayKey ? 'How do you feel today?' : 'How did you feel that day?',
)

function formatDisplayDate(dateKey) {
  if (!dateKey) {
    return ''
  }
  const [year, month, day] = dateKey.split('-').map(Number)
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'long' }).format(
    new Date(year, month - 1, day),
  )
}

function selectDate(dateKey) {
  selectedDate.value = dateKey
  resetForm()
  confirmationMessage.value = ''
  errorMessage.value = ''
}

function moveMonth(offset) {
  setVisibleMonth(shiftMonth(visibleMonth.value, offset))
}

function setVisibleMonth(monthDate) {
  visibleMonth.value = monthDate
  const isCurrentMonth =
    visibleMonth.value.getFullYear() === today.getFullYear() &&
    visibleMonth.value.getMonth() === today.getMonth()
  selectedDate.value = isCurrentMonth ? todayKey : ''
  resetForm()
  confirmationMessage.value = ''
}

function chooseMonth(event) {
  setVisibleMonth(
    new Date(visibleMonth.value.getFullYear(), Number(event.target.value), 1),
  )
}

function chooseYear(event) {
  setVisibleMonth(
    new Date(Number(event.target.value), visibleMonth.value.getMonth(), 1),
  )
}

function goToToday() {
  visibleMonth.value = new Date(today.getFullYear(), today.getMonth(), 1)
  selectDate(todayKey)
}

function markerClass(checkIn) {
  return `marker-${feelingCategory(checkIn.feeling)}`
}

function markerStyle(checkIn) {
  const fallback = FEELING_COLORS[feelingCategory(checkIn.feeling)]
  return { '--marker-color': checkIn.color || fallback }
}

function dateAriaLabel(cell) {
  const dateLabel = formatDisplayDate(cell.dateKey)
  const checkIn = checkInsByDate.value.get(cell.dateKey)
  if (checkIn) {
    return `${dateLabel}, check-in saved: ${checkIn.feeling}`
  }
  if (cell.dateKey === todayKey) {
    return `${dateLabel}, today, no check-in saved`
  }
  return `${dateLabel}, no check-in saved`
}

function resetForm() {
  selectedFeeling.value = ''
  otherFeeling.value = ''
  customColor.value = FEELING_COLORS.other
  description.value = ''
  isEditing.value = false
}

function startEditing() {
  const checkIn = selectedCheckIn.value
  if (!checkIn) {
    return
  }
  const category = feelingCategory(checkIn.feeling)
  selectedFeeling.value = category
  otherFeeling.value = category === 'other' ? checkIn.feeling : ''
  customColor.value = checkIn.color || FEELING_COLORS[category]
  description.value = checkIn.description
  isEditing.value = true
  confirmationMessage.value = ''
  errorMessage.value = ''
}

function cancelEditing() {
  resetForm()
  errorMessage.value = ''
}

async function loadCheckIns() {
  const user = accountSession.user.value
  if (!user) {
    return
  }
  isLoading.value = true
  errorMessage.value = ''
  try {
    const data = await checkInsApi.list(user.id)
    checkIns.value = data.check_ins
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

async function saveCheckIn() {
  const user = accountSession.user.value
  const feeling =
    selectedFeeling.value === 'other' ? otherFeeling.value.trim() : selectedFeeling.value
  const color =
    selectedFeeling.value === 'other'
      ? customColor.value
      : FEELING_COLORS[selectedFeeling.value]
  const trimmedDescription = description.value.trim()

  errorMessage.value = ''
  confirmationMessage.value = ''
  if (!feeling || !color || !trimmedDescription) {
    errorMessage.value = 'Choose a feeling and describe what happened before saving.'
    return
  }
  if (!user || (!canCreateSelectedDate.value && !isEditing.value)) {
    errorMessage.value = 'Choose today or an earlier date to save a check-in.'
    return
  }

  const editingAtRequest = isEditing.value
  isSaving.value = true
  try {
    const saved = editingAtRequest
      ? await checkInsApi.update(selectedCheckIn.value.id, {
          feeling,
          color,
          description: trimmedDescription,
        })
      : await checkInsApi.create(user.id, {
          feeling,
          color,
          description: trimmedDescription,
          checkInDate: selectedDate.value,
        })
    checkIns.value = editingAtRequest
      ? checkIns.value.map((checkIn) => (checkIn.id === saved.id ? saved : checkIn))
      : [...checkIns.value, saved]
    resetForm()
    confirmationMessage.value = editingAtRequest
      ? 'Your check-in was updated.'
      : 'Your check-in was saved. Its marker is now on the calendar.'
  } catch (error) {
    if (error.code === 'conflict') {
      await loadCheckIns()
      errorMessage.value = editingAtRequest
        ? 'This check-in could not be updated. Try again.'
        : 'A check-in has already been saved for this date.'
    } else {
      errorMessage.value = error.message
    }
  } finally {
    isSaving.value = false
  }
}

watch(
  () => accountSession.user.value,
  (user) => {
    if (user) {
      loadCheckIns()
    }
  },
  { immediate: true },
)
</script>

<template>
  <main class="calendar-page" data-page="calendar">
    <header class="page-heading">
      <p class="eyebrow">A moment for yourself</p>
      <h1>Daily check-in</h1>
      <p>Notice how each day feels. Add or edit past check-ins from the calendar.</p>
    </header>

    <p v-if="isLoading" class="loading-message" aria-live="polite">Loading your calendar…</p>

    <div v-else class="calendar-layout">
      <section class="calendar-card" aria-labelledby="calendar-heading">
        <div class="month-controls">
          <button type="button" aria-label="Previous month" @click="moveMonth(-1)">‹</button>
          <div id="calendar-heading" class="month-year-pickers" aria-label="Displayed calendar month and year">
            <label>
              <span class="sr-only">Choose month</span>
              <select
                class="month-select"
                :value="visibleMonth.getMonth()"
                aria-label="Choose month"
                @change="chooseMonth"
              >
                <option v-for="month in monthOptions" :key="month.value" :value="month.value">
                  {{ month.label }}
                </option>
              </select>
            </label>
            <label>
              <span class="sr-only">Choose year</span>
              <select
                class="year-select"
                :value="visibleMonth.getFullYear()"
                aria-label="Choose year"
                @change="chooseYear"
              >
                <option v-for="year in yearOptions" :key="year" :value="year">{{ year }}</option>
              </select>
            </label>
          </div>
          <button type="button" aria-label="Next month" @click="moveMonth(1)">›</button>
        </div>

        <table class="month-grid">
          <thead>
            <tr>
              <th v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" scope="col">
                {{ day }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="weekIndex in monthCells.length / 7" :key="weekIndex">
              <td
                v-for="(cell, cellIndex) in monthCells.slice((weekIndex - 1) * 7, weekIndex * 7)"
                :key="cell?.dateKey ?? `blank-${weekIndex}-${cellIndex}`"
              >
                <button
                  v-if="cell"
                  type="button"
                  class="date-button"
                  :class="{
                    'is-today': cell.dateKey === todayKey,
                    'is-selected': cell.dateKey === selectedDate,
                  }"
                  :aria-label="dateAriaLabel(cell)"
                  :aria-pressed="cell.dateKey === selectedDate"
                  @click="selectDate(cell.dateKey)"
                >
                  <span>{{ cell.day }}</span>
                  <span
                    v-if="checkInsByDate.has(cell.dateKey)"
                    class="check-in-marker"
                    :class="markerClass(checkInsByDate.get(cell.dateKey))"
                    :style="markerStyle(checkInsByDate.get(cell.dateKey))"
                    aria-hidden="true"
                  ></span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="marker-legend" aria-label="Feeling marker legend">
          <span v-for="option in feelingOptions" :key="option.value">
            <i class="check-in-marker" :class="`marker-${option.value}`"></i>{{ option.label }}
          </span>
          <span><i class="check-in-marker marker-custom"></i>Custom color</span>
        </div>
      </section>

      <section class="check-in-card" aria-labelledby="check-in-heading">
        <template v-if="selectedCheckIn && !isEditing">
          <p class="eyebrow">Saved check-in</p>
          <h2 id="check-in-heading">{{ selectedDateLabel }}</h2>
          <div class="saved-feeling">
            <span
              class="check-in-marker"
              :class="markerClass(selectedCheckIn)"
              :style="markerStyle(selectedCheckIn)"
            ></span>
            <strong>{{ selectedCheckIn.feeling }}</strong>
          </div>
          <p class="saved-description">{{ selectedCheckIn.description }}</p>
          <button class="edit-button" type="button" @click="startEditing">Edit check-in</button>
        </template>

        <form v-else-if="canCreateSelectedDate || isEditing" @submit.prevent="saveCheckIn">
          <div>
            <p class="eyebrow">{{ isEditing ? 'Edit check-in' : 'Check in' }}</p>
            <h2 id="check-in-heading">{{ formHeading }}</h2>
            <p>{{ selectedDateLabel }}</p>
          </div>

          <fieldset class="feeling-grid">
            <legend>Choose the closest feeling</legend>
            <label v-for="option in feelingOptions" :key="option.value" :class="`feeling-${option.value}`">
              <input v-model="selectedFeeling" type="radio" name="feeling" :value="option.value" />
              <span class="feeling-symbol" aria-hidden="true">{{ option.symbol }}</span>
              <span>{{ option.label }}</span>
            </label>

            <div
              class="custom-feeling-card"
              :class="{ 'is-expanded': selectedFeeling === 'other' }"
              :style="{ '--marker-color': customColor }"
            >
              <label class="custom-feeling-choice">
                <input v-model="selectedFeeling" type="radio" name="feeling" value="other" />
                <span class="feeling-symbol" aria-hidden="true">•</span>
                <span>Something else</span>
              </label>

              <div v-if="selectedFeeling === 'other'" class="custom-feeling-editor">
                <label class="text-field">
                  Name the emotion
                  <input
                    v-model="otherFeeling"
                    type="text"
                    maxlength="50"
                    autocomplete="off"
                    placeholder="For example, hopeful"
                    required
                  />
                </label>

                <fieldset class="color-field">
                  <legend>Choose its color</legend>
                  <div class="color-options">
                    <button
                      v-for="color in customColorOptions"
                      :key="color"
                      type="button"
                      class="color-swatch"
                      :class="{ 'is-selected': customColor === color }"
                      :style="{ backgroundColor: color }"
                      :aria-label="`Use color ${color}`"
                      :aria-pressed="customColor === color"
                      @click="customColor = color"
                    ></button>
                    <label class="color-picker">
                      <span>More colors</span>
                      <input v-model="customColor" type="color" aria-label="Choose a custom color" />
                    </label>
                  </div>
                </fieldset>
              </div>
            </div>
          </fieldset>

          <label class="text-field">
            Describe what happened
            <textarea
              v-model="description"
              rows="5"
              maxlength="2000"
              placeholder="Write as much or as little as feels useful."
              required
            ></textarea>
            <small>{{ description.length }}/2000</small>
          </label>

          <div class="form-actions">
            <button v-if="isEditing" class="cancel-button" type="button" :disabled="isSaving" @click="cancelEditing">
              Cancel
            </button>
            <button class="save-button" type="submit" :disabled="isSaving">
              {{ isSaving ? 'Saving…' : isEditing ? 'Update check-in' : 'Save check-in' }}
            </button>
          </div>
        </form>

        <template v-else-if="selectedDate">
          <p class="eyebrow">{{ selectedDateLabel }}</p>
          <h2 id="check-in-heading">Future check-ins aren’t available</h2>
          <p>Choose today or an earlier date to add or review a check-in.</p>
          <button class="today-button" type="button" @click="goToToday">
            Go to today
          </button>
        </template>

        <template v-else>
          <p class="eyebrow">Calendar</p>
          <h2 id="check-in-heading">Choose a date</h2>
          <p>Select a marked date to review it, or return to today to add a check-in.</p>
          <button class="today-button" type="button" @click="goToToday">
            Go to today
          </button>
        </template>

        <p v-if="confirmationMessage" class="confirmation" role="status">
          {{ confirmationMessage }}
        </p>
        <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
      </section>
    </div>
  </main>
</template>

<style scoped>
.calendar-page {
  display: grid;
  width: min(100% - 2rem, 50rem);
  gap: 1.5rem;
  margin: 0 auto;
  padding: 2.5rem 0 3rem;
}

.page-heading {
  display: grid;
  max-width: 42rem;
  gap: 0.45rem;
}

h1 {
  color: var(--color-heading);
  font-size: clamp(2rem, 7vw, 3.25rem);
  font-weight: 750;
  line-height: 1.1;
}

h2,
strong {
  color: var(--color-heading);
  font-weight: 750;
}

.eyebrow {
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 750;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.calendar-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 1.25rem;
  align-items: start;
}

.calendar-card,
.check-in-card {
  padding: clamp(1rem, 3vw, 1.5rem);
  border: 1px solid var(--color-border);
  border-radius: 1.5rem;
  background: rgba(255, 250, 242, 0.92);
  box-shadow: var(--shadow-soft);
}

.check-in-card,
.check-in-card form,
.text-field {
  display: grid;
  gap: 1rem;
}

.month-controls {
  display: grid;
  grid-template-columns: 2.75rem 1fr 2.75rem;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  text-align: center;
}

.month-controls button,
.today-button {
  min-height: 2.75rem;
  border: 1px solid var(--color-border-hover);
  border-radius: 999px;
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
  cursor: pointer;
  font-weight: 750;
}

.month-controls button {
  font-size: 1.5rem;
  line-height: 1;
}

.month-year-pickers {
  display: flex;
  min-width: 0;
  align-items: center;
  justify-content: center;
  gap: 0.15rem;
}

.month-year-pickers select {
  min-height: 2.5rem;
  padding: 0.2rem 0.35rem;
  border: 1px solid transparent;
  border-radius: 0.65rem;
  color: var(--color-heading);
  background: transparent;
  cursor: pointer;
  font-size: clamp(1.15rem, 4vw, 1.55rem);
  font-weight: 750;
}

.month-year-pickers select:hover,
.month-year-pickers select:focus-visible {
  border-color: var(--color-border-hover);
  background: var(--color-primary-soft);
}

.month-select {
  width: 9rem;
}

.year-select {
  width: 6.2rem;
}

.sr-only {
  position: absolute;
  overflow: hidden;
  width: 1px;
  height: 1px;
  padding: 0;
  border: 0;
  margin: -1px;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

.month-grid {
  width: 100%;
  border-spacing: 0.2rem;
  table-layout: fixed;
}

th {
  padding-bottom: 0.35rem;
  color: var(--color-text-soft);
  font-size: 0.72rem;
  font-weight: 700;
}

td {
  height: 3.4rem;
}

.date-button {
  position: relative;
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  padding: 0.3rem;
  border: 1px solid transparent;
  border-radius: 0.8rem;
  color: var(--color-text);
  background: transparent;
  cursor: pointer;
}

.date-button.is-today {
  border-color: var(--color-primary);
  font-weight: 800;
}

.date-button.is-selected {
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
  box-shadow: inset 0 0 0 1px var(--color-primary);
}

.check-in-marker {
  display: inline-block;
  width: 0.62rem;
  height: 0.62rem;
  flex: 0 0 auto;
  border: 1px solid rgba(40, 60, 51, 0.32);
  border-radius: 50%;
  background: var(--marker-color, var(--color-primary));
}

.date-button .check-in-marker {
  position: absolute;
  bottom: 0.32rem;
}

.marker-happy,
.feeling-happy { --marker-color: #d2a13f; }
.marker-sad,
.feeling-sad { --marker-color: #6f91aa; }
.marker-stressed,
.feeling-stressed { --marker-color: #b06d4d; }
.marker-scared,
.feeling-scared { --marker-color: #86668f; }
.marker-other,
.feeling-other { --marker-color: #66836e; }

.marker-custom {
  border: 0;
  background: conic-gradient(#496db2, #86668f, #b45f74, #d2a13f, #7b8f48, #496db2);
}

.marker-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.8rem;
  margin-top: 1rem;
  color: var(--color-text-soft);
  font-size: 0.75rem;
}

.marker-legend span,
.saved-feeling {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.feeling-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.65rem;
  padding: 0;
  border: 0;
}

.feeling-grid legend {
  grid-column: 1 / -1;
  margin-bottom: 0.25rem;
  font-weight: 700;
}

.feeling-grid > label,
.custom-feeling-choice {
  position: relative;
  display: flex;
  min-height: 3.25rem;
  align-items: center;
  gap: 0.6rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-border);
  border-left: 0.32rem solid var(--marker-color);
  border-radius: 0.85rem;
  background: var(--color-background-soft);
  cursor: pointer;
}

.feeling-grid > label:has(input:checked),
.custom-feeling-card:has(.custom-feeling-choice input:checked) {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
  box-shadow: 0 0 0 2px rgba(79, 116, 94, 0.13);
}

.custom-feeling-card {
  display: grid;
  grid-column: span 1;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-left: 0.32rem solid var(--marker-color);
  border-radius: 0.85rem;
  background: var(--color-background-soft);
  transition:
    border-color 160ms ease,
    background-color 160ms ease,
    box-shadow 160ms ease;
}

.custom-feeling-card.is-expanded {
  grid-column: 1 / -1;
}

.custom-feeling-choice {
  min-height: 3.25rem;
  border: 0;
  border-left: 0;
  border-radius: 0;
  background: transparent;
}

.custom-feeling-editor {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(13rem, 0.9fr);
  gap: 1rem;
  padding: 0 0.85rem 0.9rem;
  border-top: 1px solid color-mix(in srgb, var(--marker-color) 30%, transparent);
  padding-top: 0.9rem;
}

.color-field {
  display: grid;
  gap: 0.45rem;
  padding: 0;
  border: 0;
}

.color-field legend {
  margin-bottom: 0.35rem;
  font-weight: 700;
}

.color-options {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.55rem;
}

.color-swatch {
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: 2px solid var(--color-background-soft);
  border-radius: 50%;
  cursor: pointer;
  box-shadow: 0 0 0 1px var(--color-border-hover);
}

.color-swatch.is-selected {
  box-shadow:
    0 0 0 2px var(--color-background-soft),
    0 0 0 4px var(--color-primary-strong);
}

.color-picker {
  display: inline-flex;
  min-height: 2.25rem;
  align-items: center;
  gap: 0.45rem;
  padding: 0.25rem 0.5rem;
  border: 1px solid var(--color-border-hover);
  border-radius: 999px;
  background: var(--color-background-soft);
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 700;
}

.color-picker input {
  width: 1.75rem;
  height: 1.75rem;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
}

.feeling-symbol {
  display: grid;
  width: 1.8rem;
  height: 1.8rem;
  place-items: center;
  border-radius: 50%;
  background: color-mix(in srgb, var(--marker-color) 25%, white);
  font-weight: 800;
}

.text-field {
  gap: 0.35rem;
  font-weight: 700;
}

.text-field input,
.text-field textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border-hover);
  border-radius: 0.85rem;
  color: var(--color-text);
  background: var(--color-background-soft);
  resize: vertical;
}

.text-field small {
  color: var(--color-text-soft);
  text-align: right;
}

.save-button {
  min-height: 3rem;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  color: var(--color-on-primary);
  background: var(--color-primary);
  cursor: pointer;
  font-weight: 750;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.65rem;
}

.form-actions .save-button {
  flex: 1;
}

.cancel-button,
.edit-button {
  min-height: 3rem;
  padding: 0.55rem 1rem;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  color: var(--color-primary-strong);
  background: var(--color-background-soft);
  cursor: pointer;
  font-weight: 750;
}

.edit-button {
  width: 100%;
}

.save-button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.cancel-button:disabled {
  cursor: wait;
  opacity: 0.65;
}

.saved-feeling {
  width: fit-content;
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: var(--color-primary-soft);
  text-transform: capitalize;
}

.saved-description {
  padding: 1rem;
  border-left: 0.25rem solid var(--color-primary);
  border-radius: 0.4rem 1rem 1rem 0.4rem;
  background: var(--color-primary-soft);
  white-space: pre-wrap;
}

.confirmation,
.error-message {
  padding: 0.75rem;
  border-radius: 0.75rem;
}

.confirmation {
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
}

.error-message {
  color: var(--color-danger-strong);
  background: var(--color-danger-soft);
}

@media (max-width: 36rem) {
  .custom-feeling-editor {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 28rem) {
  .calendar-page {
    width: min(100% - 1rem, 70rem);
  }

  .calendar-card,
  .check-in-card {
    padding: 0.8rem;
    border-radius: 1rem;
  }

  td {
    height: 2.9rem;
  }

  .month-controls {
    grid-template-columns: 2.5rem 1fr 2.5rem;
  }

  .month-select {
    width: 7.4rem;
  }

  .year-select {
    width: 5.3rem;
  }

  .feeling-grid {
    grid-template-columns: 1fr;
  }

  .form-actions {
    align-items: stretch;
    flex-direction: column-reverse;
  }
}
</style>
