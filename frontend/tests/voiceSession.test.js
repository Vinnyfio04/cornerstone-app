import assert from 'node:assert/strict'
import test from 'node:test'

import { createVoiceSessionController } from '../src/voice/voiceSession.js'
import {
  SUPPORT_ACTION_EVENT,
  attachVoiceCleanup,
} from '../src/voice/voiceLifecycle.js'

const SDP_OFFER = 'v=0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\n'
const SDP_ANSWER = 'v=0\r\nm=audio 9 UDP/TLS/RTP/SAVPF 111\r\n'

function createTrack() {
  return {
    enabled: true,
    stopped: false,
    stop() {
      this.stopped = true
    },
  }
}

function createStream() {
  const track = createTrack()
  return {
    track,
    getAudioTracks() {
      return [track]
    },
    getTracks() {
      return [track]
    },
  }
}

function createBrowserHarness({ playRejects = false } = {}) {
  const operations = []
  const channels = []
  const peers = []
  const streams = []
  let rejectPlayback = playRejects

  class FakeDataChannel {
    constructor(label) {
      this.label = label
      this.readyState = 'open'
      this.sent = []
      channels.push(this)
    }

    send(value) {
      this.sent.push(JSON.parse(value))
    }

    close() {
      this.readyState = 'closed'
    }

    emit(event) {
      this.onmessage?.({ data: JSON.stringify(event) })
    }
  }

  class FakePeerConnection {
    constructor() {
      this.connectionState = 'new'
      this.iceGatheringState = 'new'
      this.listeners = new Map()
      this.localDescription = null
      this.remoteDescription = null
      this.closed = false
      peers.push(this)
    }

    createDataChannel(label) {
      operations.push(`data-channel:${label}`)
      return new FakeDataChannel(label)
    }

    addTrack(track, addedStream) {
      operations.push('add-track')
      assert.equal(track, addedStream.track)
    }

    async createOffer() {
      operations.push('create-offer')
      return { type: 'offer', sdp: SDP_OFFER }
    }

    async setLocalDescription(description) {
      operations.push('set-local-description')
      this.localDescription = description
      this.iceGatheringState = 'gathering'
      queueMicrotask(() => {
        operations.push('ice-complete')
        this.iceGatheringState = 'complete'
        this.listeners.get('icegatheringstatechange')?.()
      })
    }

    async setRemoteDescription(description) {
      operations.push('set-remote-description')
      this.remoteDescription = description
    }

    addEventListener(name, listener) {
      this.listeners.set(name, listener)
    }

    removeEventListener(name, listener) {
      if (this.listeners.get(name) === listener) {
        this.listeners.delete(name)
      }
    }

    close() {
      this.closed = true
      this.connectionState = 'closed'
    }

    emitRemoteTrack(remoteStream) {
      this.ontrack?.({ streams: [remoteStream] })
    }
  }

  const audio = {
    srcObject: null,
    paused: false,
    pause() {
      this.paused = true
    },
    async play() {
      if (rejectPlayback) {
        throw new Error('Autoplay blocked')
      }
      this.paused = false
    },
  }

  return {
    audio,
    channels,
    operations,
    peers,
    streams,
    get stream() {
      return streams[0]
    },
    mediaDevices: {
      async getUserMedia(constraints) {
        operations.push('get-user-media')
        assert.deepEqual(constraints, { audio: true, video: false })
        const stream = createStream()
        streams.push(stream)
        return stream
      },
    },
    PeerConnection: FakePeerConnection,
    allowPlayback() {
      rejectPlayback = false
    },
  }
}

function createApiHarness(operations) {
  return {
    async getConfig() {
      operations.push('get-config')
      return { status: 'configured', duration_seconds: 300 }
    },
    async createSession(sdpOffer) {
      operations.push('create-session')
      assert.equal(sdpOffer, SDP_OFFER)
      return {
        session_id: 'live_test',
        sdp_answer: SDP_ANSWER,
        duration_seconds: 300,
      }
    },
  }
}

function createDeferred() {
  let resolve
  let reject
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise
    reject = rejectPromise
  })
  return { promise, reject, resolve }
}

async function startActiveController(options = {}) {
  const browser = createBrowserHarness()
  const controller = createVoiceSessionController({
    api: options.api ?? createApiHarness(browser.operations),
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  await controller.start()
  browser.channels[0].emit({ type: 'session.started' })
  browser.peers[0].emitRemoteTrack({ id: 'remote-stream' })
  await Promise.resolve()
  assert.equal(controller.getSnapshot().status, 'active')
  return { browser, controller }
}

test('starts only on request and follows the WebRTC offer sequence', async () => {
  const browser = createBrowserHarness()
  const states = []
  const controller = createVoiceSessionController({
    api: createApiHarness(browser.operations),
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
    onChange: (state) => states.push(state.status),
  })

  assert.deepEqual(browser.operations, [])
  assert.equal(controller.getSnapshot().status, 'idle')

  await controller.start()

  assert.deepEqual(browser.operations, [
    'get-user-media',
    'get-config',
    'data-channel:oai-events',
    'add-track',
    'create-offer',
    'set-local-description',
    'ice-complete',
    'create-session',
    'set-remote-description',
  ])
  assert.equal(browser.channels[0].label, 'oai-events')
  assert.equal(controller.getSnapshot().status, 'connecting')
  assert.deepEqual(states.slice(0, 3), ['idle', 'permission', 'connecting'])

  browser.channels[0].emit({ type: 'session.started' })
  assert.equal(controller.getSnapshot().status, 'active')
  browser.peers[0].emitRemoteTrack({ id: 'remote-stream' })
  await Promise.resolve()

  controller.toggleMute()
  assert.equal(controller.getSnapshot().status, 'muted')
  assert.equal(browser.stream.track.enabled, false)
  assert.equal(browser.channels[0].sent.length, 0)
  assert.equal(browser.audio.paused, false)
  assert.equal(browser.peers[0].closed, false)
  controller.toggleMute()
  assert.equal(controller.getSnapshot().status, 'active')
  assert.equal(browser.stream.track.enabled, true)

  controller.stop()
  assert.equal(controller.getSnapshot().status, 'closing')
  assert.equal(browser.stream.track.stopped, true)
  assert.equal(browser.audio.paused, false)
  assert.equal(browser.peers[0].closed, false)
  assert.equal(browser.channels[0].sent[0].type, 'session.close')
  browser.channels[0].emit({ type: 'session.closed' })
  assert.equal(controller.getSnapshot().status, 'closed')
  assert.equal(browser.stream.track.stopped, true)
  assert.equal(browser.peers[0].closed, true)
})

test('shows a playback action when autoplay is blocked and retries from a gesture', async () => {
  const browser = createBrowserHarness({ playRejects: true })
  const controller = createVoiceSessionController({
    api: createApiHarness(browser.operations),
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  await controller.start()
  const remoteStream = { id: 'remote-stream' }
  browser.peers[0].emitRemoteTrack(remoteStream)
  await Promise.resolve()
  await Promise.resolve()

  assert.equal(browser.audio.srcObject, remoteStream)
  assert.equal(controller.getSnapshot().needsPlayback, true)

  browser.allowPlayback()
  await controller.enableAudio()
  assert.equal(controller.getSnapshot().needsPlayback, false)
  controller.dispose()
})

test('permission denial becomes a recoverable voice error without calling the API', async () => {
  let apiCalled = false
  const controller = createVoiceSessionController({
    api: {
      async getConfig() {
        apiCalled = true
      },
    },
    mediaDevices: {
      async getUserMedia() {
        const error = new Error('private permission detail')
        error.name = 'NotAllowedError'
        throw error
      },
    },
    PeerConnection: class {},
    getAudioElement: () => null,
  })

  await controller.start()

  assert.equal(controller.getSnapshot().status, 'error')
  assert.equal(
    controller.getSnapshot().errorMessage,
    'Microphone permission was denied. Text chat is still available.',
  )
  assert.equal(apiCalled, false)
})

test('API failure stops microphone tracks and exposes only a safe error', async () => {
  const browser = createBrowserHarness()
  const controller = createVoiceSessionController({
    api: {
      async getConfig() {
        throw new Error('private backend detail')
      },
    },
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  await controller.start()

  assert.equal(controller.getSnapshot().status, 'error')
  assert.equal(
    controller.getSnapshot().errorMessage,
    'Voice could not start. Text chat is still available.',
  )
  assert.equal(browser.stream.track.stopped, true)
  assert.doesNotMatch(controller.getSnapshot().errorMessage, /private backend detail/)
})

test('ignores a duplicate Start while microphone permission is pending', async () => {
  const browser = createBrowserHarness()
  const permission = createDeferred()
  let permissionRequests = 0
  const controller = createVoiceSessionController({
    api: createApiHarness(browser.operations),
    mediaDevices: {
      getUserMedia() {
        permissionRequests += 1
        return permission.promise
      },
    },
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  const firstStart = controller.start()
  await controller.start()
  assert.equal(permissionRequests, 1)
  assert.equal(controller.getSnapshot().status, 'permission')

  const stream = createStream()
  permission.resolve(stream)
  await firstStart
  assert.equal(browser.peers.length, 1)
  controller.dispose()
})

test('repeated End sends one close event and keeps playback until the short close handshake ends', async () => {
  const { browser, controller } = await startActiveController()

  controller.stop()
  controller.stop()

  assert.equal(browser.stream.track.stopped, true)
  assert.equal(browser.channels[0].sent.length, 1)
  assert.equal(browser.channels[0].sent[0].type, 'session.close')
  assert.equal(browser.audio.paused, false)
  assert.equal(browser.peers[0].closed, false)

  browser.channels[0].emit({ type: 'session.closed' })
  assert.equal(controller.getSnapshot().status, 'closed')
  assert.equal(browser.audio.paused, true)
  assert.equal(browser.peers[0].closed, true)
})

test('a late SDP answer after End is applied only to close the provider session', async () => {
  const browser = createBrowserHarness()
  const sessionResult = createDeferred()
  const sessionRequested = createDeferred()
  const api = {
    async getConfig() {
      return { status: 'configured', duration_seconds: 300 }
    },
    async createSession(sdpOffer) {
      assert.equal(sdpOffer, SDP_OFFER)
      sessionRequested.resolve()
      return sessionResult.promise
    },
  }
  const controller = createVoiceSessionController({
    api,
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  const startPromise = controller.start()
  await sessionRequested.promise
  controller.stop()
  assert.equal(controller.getSnapshot().status, 'closing')
  assert.equal(browser.stream.track.stopped, true)
  assert.equal(browser.channels[0].sent.length, 0)

  sessionResult.resolve({
    session_id: 'live_late',
    sdp_answer: SDP_ANSWER,
    duration_seconds: 300,
  })
  await startPromise

  assert.equal(browser.peers[0].remoteDescription.sdp, SDP_ANSWER)
  assert.equal(browser.channels[0].sent.length, 1)
  assert.equal(browser.channels[0].sent[0].type, 'session.close')
  assert.equal(controller.getSnapshot().status, 'closing')
  assert.equal(controller.getSnapshot().durationSeconds, null)

  browser.channels[0].emit({ type: 'session.closed' })
  assert.equal(controller.getSnapshot().status, 'closed')
})

test('the duration limit ends the microphone and provider session', async () => {
  const browser = createBrowserHarness()
  const api = {
    async getConfig() {
      return { status: 'configured', duration_seconds: 0.001 }
    },
    async createSession() {
      return {
        session_id: 'live_duration',
        sdp_answer: SDP_ANSWER,
        duration_seconds: 0.001,
      }
    },
  }
  const controller = createVoiceSessionController({
    api,
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  await controller.start()
  browser.channels[0].emit({ type: 'session.started' })
  await new Promise((resolve) => setTimeout(resolve, 20))

  assert.equal(controller.getSnapshot().status, 'closing')
  assert.equal(browser.stream.track.stopped, true)
  assert.equal(browser.channels[0].sent[0].type, 'session.close')
  browser.channels[0].emit({ type: 'session.closed' })
  assert.equal(browser.peers[0].closed, true)
})

for (const cleanupPath of [
  {
    name: 'component unmount',
    run(lifecycle) {
      lifecycle.cleanupForUnmount()
    },
  },
  {
    name: 'route navigation',
    run(lifecycle) {
      lifecycle.cleanupForNavigation()
      lifecycle.detach()
    },
  },
  {
    name: 'page exit',
    run(_lifecycle, pageTarget) {
      pageTarget.dispatchEvent(new Event('pagehide'))
    },
  },
  {
    name: 'independent crisis-support action',
    run(_lifecycle, _pageTarget, supportTarget) {
      supportTarget.dispatchEvent(new Event(SUPPORT_ACTION_EVENT))
    },
  },
]) {
  test(`cleans up voice on ${cleanupPath.name}`, async () => {
    const { browser, controller } = await startActiveController()
    const pageTarget = new EventTarget()
    const supportTarget = new EventTarget()
    const lifecycle = attachVoiceCleanup({ controller, pageTarget, supportTarget })

    cleanupPath.run(lifecycle, pageTarget, supportTarget)

    assert.equal(browser.stream.track.stopped, true)
    assert.equal(browser.channels[0].sent.length, 1)
    assert.equal(browser.channels[0].sent[0].type, 'session.close')
    assert.equal(browser.audio.paused, true)
    assert.equal(browser.audio.srcObject, null)
    assert.equal(browser.channels[0].readyState, 'closed')
    assert.equal(browser.peers[0].closed, true)
    lifecycle.detach()
  })
}

test('a completed End allows a fresh voice conversation', async () => {
  const browser = createBrowserHarness()
  const controller = createVoiceSessionController({
    api: createApiHarness(browser.operations),
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  await controller.start()
  browser.channels[0].emit({ type: 'session.started' })
  controller.stop()
  browser.channels[0].emit({ type: 'session.closed' })
  await controller.start()

  assert.equal(browser.streams.length, 2)
  assert.equal(browser.peers.length, 2)
  assert.equal(browser.channels.length, 2)
  assert.notEqual(browser.streams[0], browser.streams[1])
  assert.deepEqual(controller.getSnapshot().transcriptMessages, [])
  controller.dispose()
})

test('streams transcript events into interruptible chat bubbles', async () => {
  const { browser, controller } = await startActiveController()

  browser.channels[0].emit({
    type: 'session.output_transcript.delta',
    delta: 'Let us begin',
    start_ms: 0,
    end_ms: 400,
  })
  browser.channels[0].emit({
    type: 'session.input_transcript.delta',
    delta: 'Wait',
    start_ms: 350,
    end_ms: 600,
  })
  browser.channels[0].emit({
    type: 'session.output_transcript.delta',
    delta: 'I am listening',
    start_ms: 700,
    end_ms: 1100,
  })

  assert.deepEqual(
    controller
      .getSnapshot()
      .transcriptMessages.map(({ role, content, transcript_status: status }) => ({
        role,
        content,
        status,
      })),
    [
      { role: 'assistant', content: 'Let us begin', status: 'interrupted' },
      { role: 'user', content: 'Wait', status: 'streaming' },
      { role: 'assistant', content: 'I am listening', status: 'streaming' },
    ],
  )

  controller.stop()
  assert.equal(
    controller.getSnapshot().transcriptMessages.at(-1).transcript_status,
    'complete',
  )
  browser.channels[0].emit({
    type: 'session.output_transcript.delta',
    delta: ' ignored',
    start_ms: 1100,
    end_ms: 1200,
  })
  assert.equal(controller.getSnapshot().transcriptMessages.at(-1).content, 'I am listening')
  browser.channels[0].emit({ type: 'session.closed' })
})

test('does not display transcript events before the session is active', async () => {
  const browser = createBrowserHarness()
  const controller = createVoiceSessionController({
    api: createApiHarness(browser.operations),
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  await controller.start()
  browser.channels[0].emit({
    type: 'session.output_transcript.delta',
    delta: 'Too early',
    start_ms: 0,
    end_ms: 100,
  })

  assert.deepEqual(controller.getSnapshot().transcriptMessages, [])
  browser.channels[0].emit({ type: 'session.started' })
  browser.channels[0].emit({
    type: 'session.output_transcript.delta',
    delta: 'Now active',
    start_ms: 100,
    end_ms: 200,
  })
  assert.equal(controller.getSnapshot().transcriptMessages[0].content, 'Now active')
  controller.dispose()
})

test('duplicate Start keeps the current live transcript intact', async () => {
  const { browser, controller } = await startActiveController()
  browser.channels[0].emit({
    type: 'session.input_transcript.delta',
    delta: 'Still here',
    start_ms: 0,
    end_ms: 300,
  })

  await controller.start()

  assert.equal(controller.getSnapshot().transcriptMessages[0].content, 'Still here')
  assert.equal(browser.streams.length, 1)
  controller.dispose()
})

test('clears transient voice captions when the View starts a new text conversation', async () => {
  const { browser, controller } = await startActiveController()
  browser.channels[0].emit({
    type: 'session.input_transcript.delta',
    delta: 'Transient caption',
    start_ms: 0,
    end_ms: 300,
  })

  controller.stop()
  controller.clearTranscript()

  assert.deepEqual(controller.getSnapshot().transcriptMessages, [])
  browser.channels[0].emit({ type: 'session.closed' })
  assert.deepEqual(controller.getSnapshot().transcriptMessages, [])
})

test('ignores events from a stale data channel after a fresh Start', async () => {
  const browser = createBrowserHarness()
  const controller = createVoiceSessionController({
    api: createApiHarness(browser.operations),
    mediaDevices: browser.mediaDevices,
    PeerConnection: browser.PeerConnection,
    getAudioElement: () => browser.audio,
  })

  await controller.start()
  browser.channels[0].emit({ type: 'session.started' })
  const staleMessageHandler = browser.channels[0].onmessage
  controller.stop()
  browser.channels[0].emit({ type: 'session.closed' })
  await controller.start()
  browser.channels[1].emit({ type: 'session.started' })

  staleMessageHandler({
    data: JSON.stringify({
      type: 'session.output_transcript.delta',
      delta: 'Stale result',
      start_ms: 0,
      end_ms: 100,
    }),
  })

  assert.deepEqual(controller.getSnapshot().transcriptMessages, [])
  controller.dispose()
})
