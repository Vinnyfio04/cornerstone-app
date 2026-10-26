<script setup>
defineProps({
  message: {
    type: Object,
    required: true,
  },
})
</script>

<template>
  <article
    class="chat-message"
    :class="[`chat-message-${message.role}`, `chat-message-${message.delivery_status}`]"
    :aria-label="`${message.role} message`"
  >
    <p class="message-role">{{ message.role === 'assistant' ? 'Cornerstone' : 'You' }}</p>
    <p>{{ message.content }}</p>
    <small v-if="message.delivery_status !== 'delivered'">
      {{ message.delivery_status === 'fallback' ? 'Saved fallback' : 'Delivery failed' }}
    </small>
  </article>
</template>

<style scoped>
.chat-message {
  display: grid;
  max-width: min(88%, 36rem);
  gap: 0.35rem;
  padding: 0.85rem 1rem;
  border-radius: 1rem;
  color: var(--color-primary-strong);
  background: var(--color-secondary-soft);
  overflow-wrap: anywhere;
}

.chat-message-user {
  justify-self: end;
  color: var(--color-on-primary);
  background: var(--color-primary);
}

.chat-message-fallback,
.chat-message-failed {
  border: 2px solid var(--color-accent);
  background: var(--color-accent-soft);
  color: var(--color-warning);
}

.message-role {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

small {
  font-weight: 700;
}
</style>
