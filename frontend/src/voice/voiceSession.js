import {
  appendLiveTranscriptDelta,
  createLiveTranscriptState,
  finalizeLiveTranscript,
  resetLiveTranscript,
} from './liveTranscript.js'

const CLOSE_FALLBACK_MS = 1500
const ICE_GATHERING_TIMEOUT_MS = 10000

export const VOICE_STATUS_LABELS = Object.freeze({
  idle: 'Voice off',
  permission: 'Waiting for microphone permission',
  connecting: 'Connecting',
  active: 'Active',
  muted: 'Muted',
  closing: 'Closing',
  closed: 'Closed',
  error: 'Error',
})

function publicStartError(error) {
  if (error?.name === 'NotAllowedError' || error?.name === 'SecurityError') {
    return 'Microphone permission was denied. Text chat is still available.'
  }
  if (error?.name === 'NotFoundError') {
    return 'No microphone was found. Text chat is still available.'
  }
  return 'Voice could not start. Text chat is still available.'
}

function waitForIceGatheringComplete(peerConnection, registerCancel) {
  if (peerConnection.iceGatheringState === 'complete') {
    return Promise.resolve()
  }

  return new Promise((resolve, reject) => {
    let settled = false
    const timeoutId = globalThis.setTimeout(() => {
      cleanup()
      reject(new Error('ICE gathering timed out'))
    }, ICE_GATHERING_TIMEOUT_MS)

    function cleanup() {
      if (settled) {
        return
      }
      settled = true
      globalThis.clearTimeout(timeoutId)
      peerConnection.removeEventListener('icegatheringstatechange', handleChange)
      registerCancel(null)
    }

    function handleChange() {
      if (peerConnection.iceGatheringState !== 'complete') {
        return
      }
      cleanup()
      resolve()
    }

    registerCancel(() => {
      cleanup()
      reject(new Error('ICE gathering canceled'))
    })
    peerConnection.addEventListener('icegatheringstatechange', handleChange)
  })
}

export function createVoiceSessionController({
  api,
  getAudioElement,
  mediaDevices = globalThis.navigator?.mediaDevices,
  PeerConnection = globalThis.RTCPeerConnection,
  onChange = () => {},
} = {}) {
  let snapshot = {
    status: 'idle',
    statusLabel: VOICE_STATUS_LABELS.idle,
    errorMessage: '',
    needsPlayback: false,
    durationSeconds: null,
    transcriptMessages: [],
  }
  let transcriptState = createLiveTranscriptState()
  let runId = 0
  let localStream = null
  let peerConnection = null
  let eventChannel = null
  let durationTimer = null
  let closeTimer = null
  let cancelIceWait = null
  let sessionRequestPending = false
  let sessionCreated = false
  let remoteApplied = false
  let closeSent = false
  let endRequested = false

  function update(patch) {
    snapshot = {
      ...snapshot,
      ...patch,
    }
    snapshot.statusLabel = VOICE_STATUS_LABELS[snapshot.status]
    onChange({ ...snapshot, transcriptMessages: [...snapshot.transcriptMessages] })
  }

  function getSnapshot() {
    return { ...snapshot, transcriptMessages: [...snapshot.transcriptMessages] }
  }

  function finalizeTranscript() {
    transcriptState = finalizeLiveTranscript(transcriptState)
    return transcriptState.messages
  }

  function clearTimers() {
    if (durationTimer !== null) {
      globalThis.clearTimeout(durationTimer)
      durationTimer = null
    }
    if (closeTimer !== null) {
      globalThis.clearTimeout(closeTimer)
      closeTimer = null
    }
  }

  function stopMicrophone() {
    if (!localStream) {
      return
    }
    for (const track of localStream.getTracks()) {
      track.stop()
    }
    localStream = null
  }

  function sendSessionClose(eventPrefix = 'close') {
    if (
      closeSent ||
      !remoteApplied ||
      eventChannel?.readyState !== 'open'
    ) {
      return false
    }
    try {
      eventChannel.send(
        JSON.stringify({ type: 'session.close', event_id: `${eventPrefix}_${Date.now()}` }),
      )
      closeSent = true
      return true
    } catch {
      return false
    }
  }

  function releaseResources() {
    clearTimers()
    cancelIceWait?.()
    cancelIceWait = null

    if (eventChannel) {
      eventChannel.onopen = null
      eventChannel.onmessage = null
      eventChannel.onerror = null
      eventChannel.onclose = null
      if (eventChannel.readyState !== 'closed') {
        eventChannel.close()
      }
      eventChannel = null
    }

    if (peerConnection) {
      peerConnection.ontrack = null
      peerConnection.onconnectionstatechange = null
      peerConnection.close()
      peerConnection = null
    }

    stopMicrophone()

    const audio = getAudioElement?.()
    if (audio) {
      audio.pause?.()
      audio.srcObject = null
    }
  }

  function finishClosed() {
    const transcriptMessages = finalizeTranscript()
    runId += 1
    releaseResources()
    update({
      status: 'closed',
      errorMessage: '',
      needsPlayback: false,
      durationSeconds: null,
      transcriptMessages,
    })
  }

  function fail(error) {
    const transcriptMessages = finalizeTranscript()
    runId += 1
    releaseResources()
    update({
      status: 'error',
      errorMessage: publicStartError(error),
      needsPlayback: false,
      durationSeconds: null,
      transcriptMessages,
    })
  }

  async function tryPlayback() {
    const audio = getAudioElement?.()
    if (!audio?.srcObject) {
      return
    }

    try {
      await audio.play()
      update({ needsPlayback: false })
    } catch {
      update({ needsPlayback: true })
    }
  }

  function handleServerEvent(messageEvent, currentRun) {
    if (currentRun !== runId) {
      return
    }

    let event
    try {
      event = JSON.parse(messageEvent.data)
    } catch {
      return
    }

    if (
      event.type === 'session.started' &&
      snapshot.status === 'connecting' &&
      !endRequested
    ) {
      update({ status: 'active' })
      return
    }
    if (
      !endRequested &&
      ['active', 'muted'].includes(snapshot.status) &&
      ['session.input_transcript.delta', 'session.output_transcript.delta'].includes(
        event.type,
      )
    ) {
      const nextTranscriptState = appendLiveTranscriptDelta(transcriptState, event)
      if (nextTranscriptState !== transcriptState) {
        transcriptState = nextTranscriptState
        update({ transcriptMessages: transcriptState.messages })
      }
      return
    }
    if (event.type === 'session.closed') {
      finishClosed()
      return
    }
    if (event.type === 'error') {
      if (endRequested) {
        finishClosed()
      } else {
        fail(new Error('Live session error'))
      }
    }
  }

  async function start() {
    if (['permission', 'connecting', 'active', 'muted', 'closing'].includes(snapshot.status)) {
      return
    }

    releaseResources()
    const currentRun = ++runId
    transcriptState = resetLiveTranscript(transcriptState, {
      sessionId: currentRun,
      sessionStartedAtMs: Date.now(),
    })
    sessionRequestPending = false
    sessionCreated = false
    remoteApplied = false
    closeSent = false
    endRequested = false
    if (!api || !mediaDevices?.getUserMedia || !PeerConnection) {
      fail(new Error('Voice APIs are unavailable'))
      return
    }
    update({
      status: 'permission',
      errorMessage: '',
      needsPlayback: false,
      durationSeconds: null,
      transcriptMessages: transcriptState.messages,
    })

    try {
      const stream = await mediaDevices.getUserMedia({ audio: true, video: false })
      if (currentRun !== runId) {
        for (const track of stream.getTracks()) {
          track.stop()
        }
        return
      }
      localStream = stream
      update({ status: 'connecting' })

      const config = await api.getConfig()
      if (currentRun !== runId) {
        return
      }
      if (config.status !== 'configured') {
        throw new Error('Voice is not configured')
      }

      peerConnection = new PeerConnection()
      eventChannel = peerConnection.createDataChannel('oai-events')
      eventChannel.onopen = () => {
        if (endRequested) {
          sendSessionClose('late_open')
        }
      }
      eventChannel.onmessage = (event) => handleServerEvent(event, currentRun)
      eventChannel.onerror = () => {
        if (endRequested) {
          finishClosed()
        } else {
          fail(new Error('Voice event channel failed'))
        }
      }
      eventChannel.onclose = () => {
        if (snapshot.status === 'closing') {
          finishClosed()
        } else if (!['closed', 'error'].includes(snapshot.status)) {
          fail(new Error('Voice event channel closed'))
        }
      }

      peerConnection.onconnectionstatechange = () => {
        if (peerConnection?.connectionState === 'failed') {
          if (endRequested) {
            finishClosed()
          } else {
            fail(new Error('Voice peer connection failed'))
          }
        }
      }
      peerConnection.ontrack = (event) => {
        const audio = getAudioElement?.()
        const remoteStream = event.streams?.[0]
        if (!audio || !remoteStream) {
          return
        }
        audio.srcObject = remoteStream
        void tryPlayback()
      }

      for (const track of stream.getAudioTracks()) {
        peerConnection.addTrack(track, stream)
      }

      const offer = await peerConnection.createOffer()
      await peerConnection.setLocalDescription(offer)
      await waitForIceGatheringComplete(peerConnection, (cancel) => {
        cancelIceWait = cancel
      })
      if (currentRun !== runId) {
        return
      }

      const sdpOffer = peerConnection.localDescription?.sdp
      if (!sdpOffer) {
        throw new Error('The browser did not create an SDP offer')
      }
      sessionRequestPending = true
      let session
      try {
        session = await api.createSession(sdpOffer)
      } finally {
        sessionRequestPending = false
      }
      if (currentRun !== runId) {
        return
      }
      if (
        typeof session.sdp_answer !== 'string' ||
        !Number.isFinite(session.duration_seconds) ||
        session.duration_seconds <= 0
      ) {
        throw new Error('The server returned an invalid voice session')
      }
      sessionCreated = true
      await peerConnection.setRemoteDescription({
        type: 'answer',
        sdp: session.sdp_answer,
      })
      if (currentRun !== runId) {
        return
      }
      remoteApplied = true
      if (endRequested) {
        sendSessionClose('late_answer')
        if (closeTimer === null) {
          closeTimer = globalThis.setTimeout(finishClosed, CLOSE_FALLBACK_MS)
        }
        return
      }
      update({ durationSeconds: session.duration_seconds })
      durationTimer = globalThis.setTimeout(
        () => void stop(),
        session.duration_seconds * 1000,
      )
    } catch (error) {
      if (currentRun === runId) {
        if (endRequested) {
          finishClosed()
        } else {
          fail(error)
        }
      }
    }
  }

  function toggleMute() {
    if (!['active', 'muted'].includes(snapshot.status) || !localStream) {
      return
    }
    const shouldMute = snapshot.status === 'active'
    for (const track of localStream.getAudioTracks()) {
      track.enabled = !shouldMute
    }
    update({ status: shouldMute ? 'muted' : 'active' })
  }

  function stop() {
    if (['idle', 'closed', 'error', 'closing'].includes(snapshot.status)) {
      return
    }

    endRequested = true
    stopMicrophone()
    update({
      status: 'closing',
      errorMessage: '',
      transcriptMessages: finalizeTranscript(),
    })
    const providerMayExist = remoteApplied || sessionCreated || sessionRequestPending
    sendSessionClose()
    if (providerMayExist) {
      closeTimer = globalThis.setTimeout(finishClosed, CLOSE_FALLBACK_MS)
      return
    }
    finishClosed()
  }

  async function enableAudio() {
    await tryPlayback()
  }

  function clearTranscript() {
    transcriptState = resetLiveTranscript(transcriptState, {
      sessionId: runId,
      sessionStartedAtMs: Date.now(),
    })
    update({ transcriptMessages: transcriptState.messages })
  }

  function dispose() {
    endRequested = true
    stopMicrophone()
    sendSessionClose('dispose')
    runId += 1
    releaseResources()
  }

  onChange({ ...snapshot, transcriptMessages: [...snapshot.transcriptMessages] })

  return {
    clearTranscript,
    dispose,
    enableAudio,
    getSnapshot,
    start,
    stop,
    toggleMute,
  }
}
