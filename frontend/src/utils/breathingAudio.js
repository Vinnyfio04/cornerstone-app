export const BREATHING_AUDIO_SOURCE = '/audio/gentle-wind-chimes.mp3'

function resetAudio(audio) {
  audio.pause()
  audio.currentTime = 0
}

export function createBreathingAudioController({
  createAudio = (source) => new Audio(source),
} = {}) {
  const audio = createAudio(BREATHING_AUDIO_SOURCE)
  audio.preload = 'auto'
  audio.loop = true

  let isPlaying = false

  function stop() {
    isPlaying = false
    resetAudio(audio)
  }

  function play() {
    if (isPlaying) {
      return
    }

    isPlaying = true
    audio.currentTime = 0
    audio.play()?.catch(() => {
      isPlaying = false
    })
  }

  return {
    play,
    stop,
  }
}
