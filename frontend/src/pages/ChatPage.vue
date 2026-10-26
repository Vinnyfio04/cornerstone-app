<script setup>
import { onBeforeUnmount, ref, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'

import { chatApi } from '../api/chat.js'
import { voiceApi } from '../api/voice.js'
import ChatMessage from '../components/ChatMessage.vue'
import { useDemoUserSession } from '../session/demoUser.js'
import { createVoiceSessionController } from '../voice/voiceSession.js'
import { attachVoiceCleanup } from '../voice/voiceLifecycle.js'

const demoUserSession = useDemoUserSession()
const conversationId = ref(null)
const messages = ref([])
const draft = ref('')
const failedDraft = ref('')
const chatMode = ref('mock')
const isLoading = ref(false)
const isSending = ref(false)
const errorMessage = ref('')
const remoteAudio = ref(null)
const voiceState = ref({
  status: 'idle',
  statusLabel: 'Voice off',
  errorMessage: '',
  needsPlayback: false,
  durationSeconds: null,
})

const voiceController = createVoiceSessionController({
  api: voiceApi,
  getAudioElement: () => remoteAudio.value,
  onChange: (state) => {
    voiceState.value = state
  },
})
const voiceCleanup = attachVoiceCleanup({ controller: voiceController })

async function loadLatestConversation() {
  const user = demoUserSession.user.value
  if (!user) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  try {
    const data = await chatApi.listConversations(user.id)
    const latest = data.conversations[0]
    if (!latest) {
      conversationId.value = null
      messages.value = []
      return
    }
    conversationId.value = latest.id
    const messageData = await chatApi.listMessages(latest.id)
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
  errorMessage.value = ''
  failedDraft.value = content
  draft.value = ''

  try {
    const data = await chatApi.send(user.id, content, conversationId.value)
    conversationId.value = data.conversation_id
    chatMode.value = data.chat_mode
    messages.value.push(data.user_message, data.assistant_message)
    failedDraft.value = ''
  } catch (error) {
    chatMode.value = 'unavailable'
    errorMessage.value = error.message
    await loadLatestConversation()
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

function startVoice() {
  void voiceController.start()
}

function stopVoice() {
  voiceController.stop()
}

function toggleVoiceMute() {
  voiceController.toggleMute()
}

function enableAssistantAudio() {
  void voiceController.enableAudio()
}

watch(
  () => demoUserSession.user.value,
  (user) => {
    if (user) {
      loadLatestConversation()
    }
  },
  { immediate: true },
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
      <p>Mock mode is deterministic by default. This prototype is not therapy or monitoring.</p>
    </header>

    <p class="mode-label">Provider mode: {{ chatMode }}</p>

    <section class="voice-card" aria-labelledby="voice-title">
      <div class="voice-heading">
        <div>
          <p class="eyebrow">Optional spoken interaction</p>
          <h2 id="voice-title">Use your microphone</h2>
        </div>
        <p class="voice-status" :data-status="voiceState.status" aria-live="polite">
          {{ voiceState.statusLabel }}
        </p>
      </div>

      <p id="voice-description">
        Voice starts only when you choose the microphone. Text chat stays available if permission
        is denied or voice cannot connect.
      </p>
      <p class="voice-detail">
        Mute affects only your microphone. Assistant audio and provider usage continue until you
        choose End.
      </p>
      <p v-if="voiceState.durationSeconds" class="voice-detail">
        Session limit: {{ voiceState.durationSeconds }} seconds
      </p>
      <p v-if="voiceState.errorMessage" class="voice-error" role="alert">
        {{ voiceState.errorMessage }}
      </p>

      <div class="voice-actions">
        <button
          v-if="['idle', 'closed', 'error'].includes(voiceState.status)"
          type="button"
          aria-describedby="voice-description"
          @click="startVoice"
        >
          {{ voiceState.status === 'error' ? 'Try microphone again' : 'Start voice' }}
        </button>
        <button
          v-if="['permission', 'connecting'].includes(voiceState.status)"
          type="button"
          class="button-secondary"
          @click="stopVoice"
        >
          End
        </button>
        <button
          v-if="['active', 'muted'].includes(voiceState.status)"
          type="button"
          class="button-secondary"
          @click="toggleVoiceMute"
        >
          {{ voiceState.status === 'muted' ? 'Unmute' : 'Mute' }}
        </button>
        <button
          v-if="['active', 'muted'].includes(voiceState.status)"
          type="button"
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
          Enable assistant audio
        </button>
        <button v-if="voiceState.status === 'closing'" type="button" disabled>
          Closing…
        </button>
      </div>

      <audio ref="remoteAudio" autoplay playsinline aria-hidden="true"></audio>
    </section>

    <section class="message-list" aria-label="Conversation messages" aria-live="polite">
      <p v-if="isLoading">Loading saved conversation…</p>
      <p v-else-if="messages.length === 0" class="empty-message">
        No saved messages yet. Describe a fictional scenario to exercise the chat flow.
      </p>
      <ChatMessage v-for="message in messages" :key="message.id" :message="message" />
      <p v-if="isSending">Creating and saving a response…</p>
    </section>

    <aside v-if="errorMessage" class="error-card" role="alert">
      <p>{{ errorMessage }}</p>
      <div>
        <button v-if="failedDraft" type="button" @click="retryMessage">Retry message</button>
        <button type="button" @click="loadLatestConversation">Reload saved messages</button>
      </div>
    </aside>

    <form class="chat-form" @submit.prevent="sendMessage()">
      <label for="chat-draft">Message</label>
      <textarea
        id="chat-draft"
        v-model="draft"
        maxlength="2000"
        rows="4"
        :disabled="!demoUserSession.user.value || isSending"
        placeholder="Write a fictional scenario…"
      />
      <div class="composer-footer">
        <small>{{ draft.length }} / 2000</small>
        <button
          type="submit"
          :disabled="!demoUserSession.user.value || !draft.trim() || isSending"
        >
          Send message
        </button>
      </div>
    </form>
  </main>
</template>

<style scoped>
.chat-page {
  display: grid;
  width: min(100% - 2rem, 48rem);
  gap: 1.25rem;
  margin: 0 auto;
  padding: 2.5rem 0 3rem;
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

.message-list {
  display: grid;
  min-height: 14rem;
  align-content: start;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: var(--color-background-soft);
  box-shadow: var(--shadow-soft);
}

.voice-card {
  display: grid;
  gap: 0.85rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  border-color: var(--color-secondary);
  background: linear-gradient(135deg, var(--color-background-soft), var(--color-secondary-soft));
  box-shadow: var(--shadow-soft);
}

.voice-heading,
.voice-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
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

.voice-detail {
  color: var(--color-text-soft);
  font-size: 0.88rem;
}

.voice-actions {
  justify-content: flex-start;
  flex-wrap: wrap;
}

.button-secondary {
  border-color: var(--color-secondary-strong);
  color: var(--color-secondary-strong);
  background: var(--color-background-soft);
}

.empty-message {
  align-self: center;
  text-align: center;
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

.error-card div,
.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.chat-form {
  display: grid;
  gap: 0.5rem;
}

label {
  font-weight: 700;
}

textarea {
  width: 100%;
  padding: 0.8rem;
  border: 2px solid var(--color-border-hover);
  border-radius: 0.75rem;
  color: var(--color-text);
  background: var(--color-background-soft);
  font: inherit;
  resize: vertical;
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
textarea:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

button:focus-visible,
textarea:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

@media (max-width: 34rem) {
  .error-card div,
  .composer-footer,
  .voice-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .voice-status {
    align-self: flex-start;
  }
}
</style>
