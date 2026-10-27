<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'

import { chatApi } from '../api/chat.js'
import { voiceApi } from '../api/voice.js'
import ChatMessage from '../components/ChatMessage.vue'
import { useDemoUserSession } from '../session/demoUser.js'
import { selectConversation } from '../utils/conversationSelection.js'
import {
  createPendingUserMessage,
  reconcilePendingMessage,
  removePendingMessage,
} from '../utils/optimisticChat.js'
import { createVoiceSessionController } from '../voice/voiceSession.js'
import { attachVoiceCleanup } from '../voice/voiceLifecycle.js'

const demoUserSession = useDemoUserSession()
const route = useRoute()
const router = useRouter()
const conversationId = ref(null)
const messages = ref([])
const draft = ref('')
const failedDraft = ref('')
const chatMode = ref('openai')
const isLoading = ref(false)
const isSending = ref(false)
const errorMessage = ref('')
const remoteAudio = ref(null)
const messageListElement = ref(null)
const voiceState = ref({
  status: 'idle',
  statusLabel: 'Voice off',
  errorMessage: '',
  needsPlayback: false,
  durationSeconds: null,
  transcriptMessages: [],
})
const voiceAnnouncement = ref('')
const shouldFollowLatestMessage = ref(true)
let pendingMessageSequence = 0
const displayMessages = computed(() => {
  const timestampFor = (message) => {
    if (message.source === 'voice') {
      return Date.parse(message.created_at)
    }

    const timestamp = Date.parse(`${message.created_at?.replace(' ', 'T')}Z`)
    return Number.isFinite(timestamp) ? timestamp : 0
  }

  return [...messages.value, ...voiceState.value.transcriptMessages]
    .map((message, index) => ({ message, index, timestamp: timestampFor(message) }))
    .sort((left, right) => left.timestamp - right.timestamp || left.index - right.index)
    .map(({ message }) => message)
})
const conversationSaveLabel = computed(() =>
  conversationId.value
    ? `Conversation ${conversationId.value} · saved automatically`
    : 'New conversation · saved after your first message',
)
const microphoneButtonLabel = computed(() => {
  if (voiceState.value.status === 'active') {
    return 'Mute microphone'
  }

  if (voiceState.value.status === 'muted') {
    return 'Unmute microphone'
  }

  if (voiceState.value.status === 'error') {
    return 'Try voice again'
  }

  if (['permission', 'connecting', 'closing'].includes(voiceState.value.status)) {
    return voiceState.value.statusLabel
  }

  return 'Start voice'
})
const isMicrophoneButtonDisabled = computed(() =>
  ['permission', 'connecting', 'closing'].includes(voiceState.value.status),
)
const showVoiceSessionBar = computed(
  () =>
    !['idle', 'closed'].includes(voiceState.value.status) || voiceState.value.needsPlayback,
)

const voiceController = createVoiceSessionController({
  api: voiceApi,
  getAudioElement: () => remoteAudio.value,
  onChange: (state) => {
    const previousMessages = new Map(
      voiceState.value.transcriptMessages.map((message) => [message.id, message]),
    )
    const completedMessage = state.transcriptMessages.find(
      (message) =>
        message.transcript_status !== 'streaming' &&
        previousMessages.get(message.id)?.transcript_status === 'streaming',
    )

    voiceState.value = state
    if (completedMessage) {
      voiceAnnouncement.value = `${completedMessage.role === 'assistant' ? 'Cornerstone' : 'Your'} voice message is complete.`
    }
  },
})
const voiceCleanup = attachVoiceCleanup({ controller: voiceController })

async function loadLatestConversation({ recoverLatest = false } = {}) {
  const user = demoUserSession.user.value
  if (!user) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  try {
    const data = await chatApi.listConversations(user.id)
    const selection = selectConversation(data.conversations, {
      requestedId: recoverLatest
        ? conversationId.value
          ? String(conversationId.value)
          : undefined
        : route.query.conversation,
      startNew: !recoverLatest && route.query.new === '1',
    })

    if (selection.status === 'unavailable') {
      conversationId.value = null
      messages.value = []
      errorMessage.value = 'That saved conversation is unavailable for this demo account.'
      return
    }

    if (!selection.conversation) {
      conversationId.value = null
      messages.value = []
      return
    }

    conversationId.value = selection.conversation.id
    const messageData = await chatApi.listMessages(selection.conversation.id)
    messages.value = messageData.messages
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isLoading.value = false
  }
}

async function sendMessage(messageText = draft.value) {
  const user = demoUserSession.user.value
  const content = messageText.trim()
  if (!user || !content || isSending.value) {
    return
  }

  isSending.value = true
  shouldFollowLatestMessage.value = true
  errorMessage.value = ''
  failedDraft.value = content
  draft.value = ''
  pendingMessageSequence += 1
  const pendingMessage = createPendingUserMessage(
    content,
    `pending-${Date.now()}-${pendingMessageSequence}`,
  )
  messages.value.push(pendingMessage)

  try {
    const data = await chatApi.send(user.id, content, conversationId.value)
    conversationId.value = data.conversation_id
    chatMode.value = data.chat_mode
    messages.value = reconcilePendingMessage(
      messages.value,
      pendingMessage.id,
      data.user_message,
      data.assistant_message,
    )
    failedDraft.value = ''
    if (route.query.conversation !== String(data.conversation_id)) {
      void router.replace({
        name: 'chat',
        query: { conversation: String(data.conversation_id) },
      })
    }
  } catch (error) {
    messages.value = removePendingMessage(messages.value, pendingMessage.id)
    chatMode.value = 'unavailable'
    errorMessage.value = error.message
    await loadLatestConversation({ recoverLatest: true })
    errorMessage.value = error.message
  } finally {
    isSending.value = false
  }
}

function retryMessage() {
  const content = failedDraft.value
  failedDraft.value = ''
  sendMessage(content)
}

function startNewConversation() {
  if (!['idle', 'closed', 'error'].includes(voiceState.value.status)) {
    voiceController.stop()
  }
  voiceController.clearTranscript()
  conversationId.value = null
  messages.value = []
  draft.value = ''
  failedDraft.value = ''
  errorMessage.value = ''
  shouldFollowLatestMessage.value = true
  void router.push({ name: 'chat', query: { new: '1' } })
}

function startVoice() {
  shouldFollowLatestMessage.value = true
  void voiceController.start()
}

function stopVoice() {
  voiceController.stop()
}

function toggleVoiceMute() {
  voiceController.toggleMute()
}

function handleMicrophoneButton() {
  if (['active', 'muted'].includes(voiceState.value.status)) {
    toggleVoiceMute()
    return
  }

  startVoice()
}

function enableAssistantAudio() {
  void voiceController.enableAudio()
}

function scrollToLatestMessage() {
  void nextTick(() => {
    if (messageListElement.value && shouldFollowLatestMessage.value) {
      messageListElement.value.scrollTop = messageListElement.value.scrollHeight
    }
  })
}

function handleMessageListScroll() {
  const element = messageListElement.value
  if (!element) {
    return
  }

  const distanceFromBottom = element.scrollHeight - element.scrollTop - element.clientHeight
  shouldFollowLatestMessage.value = distanceFromBottom <= 80
}

watch(
  [
    () => demoUserSession.user.value,
    () => route.query.conversation,
    () => route.query.new,
  ],
  ([user]) => {
    if (user) {
      loadLatestConversation()
    }
  },
  { immediate: true },
)

watch(
  [
    () =>
      displayMessages.value
        .map(
          (message) =>
            `${message.source ?? 'text'}:${message.id}:${message.content.length}:${message.transcript_status ?? ''}`,
        )
        .join('|'),
    isSending,
  ],
  scrollToLatestMessage,
)

onBeforeRouteLeave(() => {
  voiceCleanup.cleanupForNavigation()
})

onBeforeUnmount(() => {
  voiceCleanup.cleanupForUnmount()
})
</script>

<template>
  <main class="chat-page" data-page="chat">
    <header>
      <p class="eyebrow">Fictional demo conversation</p>
      <h1>Chat</h1>
      <p>
        Text responses use the server-configured OpenAI model. This prototype is not therapy or
        monitoring.
      </p>
    </header>

    <div class="conversation-toolbar">
      <div>
        <p class="mode-label">Model connection: {{ chatMode }}</p>
        <p class="save-label">{{ conversationSaveLabel }}</p>
      </div>
      <button type="button" class="button-secondary" @click="startNewConversation">
        New conversation
      </button>
    </div>

    <aside v-if="errorMessage" class="error-card" role="alert">
      <p>{{ errorMessage }}</p>
      <div>
        <button v-if="failedDraft" type="button" @click="retryMessage">Retry message</button>
        <button type="button" @click="loadLatestConversation">Reload saved messages</button>
      </div>
    </aside>

    <section class="chat-window" aria-label="Text and voice conversation">
      <p class="visually-hidden" aria-live="polite">{{ voiceAnnouncement }}</p>
      <div
        ref="messageListElement"
        class="message-list"
        role="log"
        aria-label="Conversation messages"
        aria-live="polite"
        @scroll="handleMessageListScroll"
      >
        <p v-if="isLoading">Loading saved conversation…</p>
        <p v-else-if="displayMessages.length === 0" class="empty-message">
          {{
            conversationId
              ? 'This saved conversation has no messages.'
              : 'Start a new fictional conversation. It will save automatically after you send.'
          }}
        </p>
        <ChatMessage
          v-for="message in displayMessages"
          :key="`${message.source ?? 'text'}-${message.id}`"
          :message="message"
        />
        <p v-if="isSending" class="sending-message">Cornerstone is responding…</p>
      </div>

      <form class="chat-form" @submit.prevent="sendMessage()">
        <label class="visually-hidden" for="chat-draft">Message</label>
        <div class="composer-field">
          <input
            id="chat-draft"
            v-model="draft"
            type="text"
            maxlength="2000"
            :disabled="!demoUserSession.user.value || isSending"
            placeholder="Write a message…"
          />
          <small class="character-count">{{ draft.length }} / 2000</small>
        </div>
        <p id="voice-description" class="visually-hidden">
          Voice starts only when you choose the microphone. Muting affects only your microphone;
          assistant audio and provider usage continue until you choose End.
        </p>
        <button
          type="button"
          class="microphone-button"
          :class="{
            'microphone-button-active': voiceState.status === 'active',
            'microphone-button-muted': voiceState.status === 'muted',
            'microphone-button-error': voiceState.status === 'error',
          }"
          :aria-label="microphoneButtonLabel"
          :title="microphoneButtonLabel"
          aria-describedby="voice-description"
          :disabled="isMicrophoneButtonDisabled"
          @click="handleMicrophoneButton"
        >
          <svg aria-hidden="true" viewBox="0 0 24 24">
            <rect x="9" y="3" width="6" height="11" rx="3" />
            <path d="M6.5 11.5a5.5 5.5 0 0 0 11 0M12 17v4M9 21h6" />
          </svg>
        </button>
        <button
          type="submit"
          :disabled="!demoUserSession.user.value || !draft.trim() || isSending"
        >
          Send
        </button>
      </form>

      <div v-if="showVoiceSessionBar" class="voice-session-bar" aria-live="polite">
        <div class="voice-session-summary">
          <span class="voice-status" :data-status="voiceState.status">
            {{ voiceState.statusLabel }}
          </span>
          <small v-if="voiceState.durationSeconds">
            {{ voiceState.durationSeconds }} second limit
          </small>
          <small v-if="['active', 'muted'].includes(voiceState.status)">
            Muting does not stop assistant audio or provider usage.
          </small>
        </div>
        <p v-if="voiceState.errorMessage" class="voice-error" role="alert">
          {{ voiceState.errorMessage }}
        </p>
        <div class="voice-session-actions">
          <button
            v-if="['permission', 'connecting', 'active', 'muted'].includes(voiceState.status)"
            type="button"
            class="button-secondary"
            @click="stopVoice"
          >
            End
          </button>
          <button
            v-if="voiceState.needsPlayback"
            type="button"
            class="button-secondary"
            @click="enableAssistantAudio"
          >
            Enable audio
          </button>
        </div>
      </div>

      <audio ref="remoteAudio" autoplay playsinline aria-hidden="true"></audio>
    </section>
  </main>
</template>

<style scoped>
.chat-page {
  display: grid;
  width: min(100% - 2rem, 52rem);
  gap: 1rem;
  margin: 0 auto;
  padding: 2rem 0 2.5rem;
}

header {
  display: grid;
  gap: 0.4rem;
}

h1 {
  color: var(--color-heading);
  font-size: clamp(2rem, 7vw, 3rem);
  font-weight: 750;
}

h2 {
  color: var(--color-heading);
  font-size: 1.25rem;
  font-weight: 750;
}

.eyebrow,
.mode-label {
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 750;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.conversation-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.save-label {
  margin-top: 0.2rem;
  color: var(--color-text-soft);
  font-size: 0.85rem;
}

.message-list {
  display: grid;
  min-height: 22rem;
  max-height: min(56vh, 36rem);
  align-content: start;
  gap: 0.75rem;
  padding: 1.25rem;
  overflow-y: auto;
  background:
    linear-gradient(rgba(255, 250, 242, 0.78), rgba(255, 250, 242, 0.78)),
    var(--color-secondary-soft);
  scrollbar-color: var(--color-border-hover) transparent;
}

.chat-window {
  overflow: hidden;
  border: 1px solid var(--color-border-hover);
  border-radius: 1.35rem;
  background: var(--color-background-soft);
  box-shadow: var(--shadow-raised);
}

.voice-status {
  flex: 0 0 auto;
  padding: 0.25rem 0.65rem;
  border: 1px solid var(--color-border-hover);
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 700;
}

.voice-status[data-status='active'] {
  border-color: var(--color-primary);
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
}

.voice-status[data-status='muted'],
.voice-status[data-status='closing'] {
  border-color: var(--color-accent);
  color: var(--color-warning);
  background: var(--color-warning-soft);
}

.voice-status[data-status='error'],
.voice-error {
  color: var(--color-danger);
}

.button-secondary {
  border-color: var(--color-secondary-strong);
  color: var(--color-secondary-strong);
  background: var(--color-background-soft);
}

.empty-message {
  align-self: center;
  max-width: 24rem;
  justify-self: center;
  color: var(--color-text-soft);
  text-align: center;
}

.sending-message {
  justify-self: start;
  padding: 0.55rem 0.8rem;
  border-radius: 1rem 1rem 1rem 0.3rem;
  color: var(--color-text-soft);
  background: var(--color-secondary-soft);
  font-size: 0.85rem;
  font-style: italic;
}

.error-card {
  display: grid;
  gap: 0.75rem;
  padding: 1rem;
  border: 2px solid var(--color-danger);
  border-radius: 1rem;
  color: var(--color-danger-strong);
  background: var(--color-danger-soft);
}

.error-card div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.chat-form {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: stretch;
  gap: 0.65rem;
  padding: 0.7rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-background-soft);
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}

.composer-field {
  position: relative;
  min-width: 0;
}

input {
  display: block;
  width: 100%;
  min-height: 3.4rem;
  padding: 0.65rem 0.75rem 1.25rem;
  border: 1px solid var(--color-border-hover);
  border-radius: 1rem;
  color: var(--color-text);
  background: var(--color-background);
  font: inherit;
}

.character-count {
  position: absolute;
  right: 0.75rem;
  bottom: 0.25rem;
  color: var(--color-text-soft);
  font-size: 0.68rem;
  pointer-events: none;
}

.chat-form > button {
  min-width: 5rem;
  align-self: stretch;
}

.chat-form > .microphone-button {
  display: grid;
  width: 3.4rem;
  min-width: 3.4rem;
  padding: 0;
  place-items: center;
  border-color: var(--color-secondary-strong);
  color: var(--color-secondary-strong);
  background: var(--color-secondary-soft);
}

.microphone-button svg {
  width: 1.35rem;
  height: 1.35rem;
  overflow: visible;
  fill: currentcolor;
}

.microphone-button path {
  fill: none;
  stroke: currentcolor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.chat-form > .microphone-button-active {
  border-color: var(--color-primary);
  color: var(--color-on-primary);
  background: var(--color-primary);
  box-shadow: 0 0 0 0.25rem var(--color-primary-soft);
}

.chat-form > .microphone-button-muted {
  border-color: var(--color-accent);
  color: var(--color-warning);
  background: var(--color-warning-soft);
}

.chat-form > .microphone-button-error {
  border-color: var(--color-danger);
  color: var(--color-danger);
  background: var(--color-danger-soft);
}

.voice-session-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-secondary-soft);
}

.voice-session-summary {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.4rem 0.65rem;
}

.voice-session-summary small {
  color: var(--color-text-soft);
}

.voice-session-actions {
  display: flex;
  flex: 0 0 auto;
  gap: 0.45rem;
}

.voice-session-actions button {
  min-height: 2.25rem;
  padding: 0.35rem 0.75rem;
}

button {
  min-height: 2.75rem;
  padding: 0.55rem 1rem;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  color: var(--color-on-primary);
  background: var(--color-primary);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

button:disabled,
input:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

button:focus-visible,
input:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

@media (max-width: 34rem) {
  .error-card div,
  .conversation-toolbar,
  .voice-session-bar {
    align-items: stretch;
    flex-direction: column;
  }

  .message-list {
    min-height: 18rem;
    padding: 0.85rem;
  }

  .chat-form {
    gap: 0.45rem;
    padding: 0.55rem;
  }

  .chat-form > button {
    min-width: 4rem;
    padding-inline: 0.7rem;
  }

  .chat-form > .microphone-button {
    width: 3.25rem;
    min-width: 3.25rem;
    padding: 0;
  }

  .voice-session-actions {
    align-self: flex-start;
  }
}
</style>
