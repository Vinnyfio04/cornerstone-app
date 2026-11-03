<script setup>
import { ref, watch } from 'vue'

import { chatApi } from '../api/chat.js'
import ChatMessage from './ChatMessage.vue'

const props = defineProps({
  userId: { type: Number, default: null },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['select'])
const dropdown = ref(null)
const conversations = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

function conversationTitle(conversation) {
  const content = conversation.messages.find((message) => message.role === 'user')?.content.trim()
  if (!content) return `Conversation ${conversation.id}`
  return content.length > 64 ? `${content.slice(0, 61)}…` : content
}

function formatDate(timestamp) {
  if (!timestamp) return 'Date unavailable'
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(timestamp))
}

async function loadConversations() {
  const userId = props.userId
  if (!userId || isLoading.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    const data = await chatApi.listConversations(userId)
    const saved = await Promise.all(
      data.conversations.map(async (conversation) => {
        const result = await chatApi.listMessages(conversation.id)
        return { ...conversation, messages: result.messages }
      }),
    )
    if (props.userId === userId) conversations.value = saved
  } catch (error) {
    if (props.userId === userId) errorMessage.value = error.message
  } finally {
    if (props.userId === userId) isLoading.value = false
  }
}

function handleToggle(event) {
  if (event.target !== event.currentTarget) return
  if (dropdown.value?.open) void loadConversations()
}

function selectConversation(id) {
  if (props.disabled) return
  dropdown.value.open = false
  emit('select', id)
}

function closeDropdown() {
  if (dropdown.value) dropdown.value.open = false
}

watch(() => props.userId, () => {
  closeDropdown()
  conversations.value = []
  errorMessage.value = ''
  isLoading.value = false
})

watch(() => props.disabled, (disabled) => {
  if (disabled) closeDropdown()
})
</script>

<template>
  <details ref="dropdown" class="past-conversations" @toggle="handleToggle" @keydown.esc.stop="closeDropdown">
    <summary
      :aria-disabled="disabled"
      :tabindex="disabled ? -1 : 0"
      @click="disabled && $event.preventDefault()"
    >
      Past conversations
    </summary>
    <section class="conversation-dropdown" aria-label="Past conversations">
      <h2>Past conversations</h2>
      <p>Messages save automatically and can be reopened to continue the same chat.</p>
      <p v-if="isLoading" role="status">Loading past conversations…</p>
      <div v-else-if="errorMessage" role="alert">
        <p>{{ errorMessage }}</p>
        <button type="button" @click="loadConversations">Retry past conversations</button>
      </div>
      <p v-else-if="conversations.length === 0">No saved conversations yet.</p>
      <ol v-else class="conversation-list">
        <li v-for="conversation in conversations" :key="conversation.id">
          <details class="conversation-card">
            <summary>{{ conversationTitle(conversation) }}</summary>
            <div class="conversation-meta">
              <small>
                Updated {{ formatDate(conversation.updated_at) }} ·
                {{ conversation.messages.length }} messages
              </small>
              <button type="button" :disabled="disabled" @click="selectConversation(conversation.id)">
                Open conversation
              </button>
            </div>
            <div class="conversation-messages">
              <ChatMessage v-for="message in conversation.messages" :key="message.id" :message="message" />
            </div>
          </details>
        </li>
      </ol>
    </section>
  </details>
</template>

<style scoped>
.past-conversations {
  position: relative;
  min-width: 0;
}

.past-conversations > summary,
button {
  min-height: 2.75rem;
  padding: 0.55rem 1rem;
  border: 2px solid var(--color-secondary-strong);
  border-radius: 999px;
  color: var(--color-secondary-strong);
  background: var(--color-background-soft);
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.past-conversations > summary {
  white-space: nowrap;
}

summary[aria-disabled='true'],
button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

summary:focus-visible,
button:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

.conversation-dropdown {
  position: absolute;
  z-index: 5;
  top: calc(100% + 0.5rem);
  right: 0;
  display: grid;
  width: min(34rem, calc(100vw - 3rem));
  max-height: min(65vh, 38rem);
  gap: 0.75rem;
  padding: 1rem;
  overflow: auto;
  border: 1px solid var(--color-border-hover);
  border-radius: 1rem;
  color: var(--color-text);
  background: var(--color-background);
  box-shadow: var(--shadow-raised);
}

h2 {
  color: var(--color-heading);
  font-size: 1.1rem;
  font-weight: 750;
}

.conversation-list,
.conversation-messages {
  display: grid;
  gap: 0.75rem;
}

.conversation-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.conversation-card {
  padding: 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: 0.85rem;
  background: var(--color-background-soft);
}

.conversation-card summary {
  overflow-wrap: anywhere;
  cursor: pointer;
  font-weight: 700;
}

.conversation-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-block: 0.75rem;
}

.conversation-meta button {
  min-height: 2.25rem;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
}

@media (max-width: 48rem) {
  .conversation-dropdown {
    right: auto;
    left: 0;
  }
}
</style>
