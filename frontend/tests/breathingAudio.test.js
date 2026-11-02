import assert from 'node:assert/strict'
import test from 'node:test'

import {
  BREATHING_AUDIO_SOURCE,
  createBreathingAudioController,
} from '../src/utils/breathingAudio.js'

function createAudioHarness({ rejectPlay = false } = {}) {
  const audioBySource = new Map()

  function createAudio(source) {
    const audio = {
      currentTime: 12,
      loop: false,
      pauseCalls: 0,
      playCalls: 0,
      playbackRate: 1,
      preload: 'none',
      preservesPitch: false,
      pause() {
        this.pauseCalls += 1
      },
      play() {
        this.playCalls += 1
        return rejectPlay ? Promise.reject(new Error('Autoplay blocked')) : Promise.resolve()
      },
    }

    audioBySource.set(source, audio)
    return audio
  }

  return { audioBySource, createAudio }
}

test('preloads and loops the wind-chime ambience without changing playback speed', () => {
  const harness = createAudioHarness()
  createBreathingAudioController({ createAudio: harness.createAudio })
  const audio = harness.audioBySource.get(BREATHING_AUDIO_SOURCE)

  assert.equal(audio.preload, 'auto')
  assert.equal(audio.loop, true)
  assert.equal(audio.playbackRate, 1)
  assert.equal(audio.preservesPitch, false)
})

test('plays the ambience once while the exercise remains active', () => {
  const harness = createAudioHarness()
  const controller = createBreathingAudioController({ createAudio: harness.createAudio })
  const audio = harness.audioBySource.get(BREATHING_AUDIO_SOURCE)

  controller.play()
  controller.play()

  assert.equal(audio.playCalls, 1)
  assert.equal(audio.currentTime, 0)
})

test('stops and rewinds the ambience', () => {
  const harness = createAudioHarness()
  const controller = createBreathingAudioController({ createAudio: harness.createAudio })
  const audio = harness.audioBySource.get(BREATHING_AUDIO_SOURCE)

  controller.play()
  audio.currentTime = 3
  controller.stop()

  assert.equal(audio.currentTime, 0)
  assert.ok(audio.pauseCalls >= 1)
})

test('continues safely when ambience playback is blocked', async () => {
  const harness = createAudioHarness({ rejectPlay: true })
  const controller = createBreathingAudioController({ createAudio: harness.createAudio })

  assert.doesNotThrow(() => controller.play())
  await new Promise((resolve) => setTimeout(resolve, 0))
})
