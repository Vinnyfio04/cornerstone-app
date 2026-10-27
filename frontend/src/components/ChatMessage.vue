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
    :class="[
      `chat-message-${message.role}`,
      `chat-message-${message.delivery_status}`,
      {
        'chat-message-live': message.source === 'voice',
        'chat-message-streaming': message.transcript_status === 'streaming',
      },
    ]"
    :aria-label="`${message.role} message`"
    :aria-busy="message.transcript_status === 'streaming' || message.delivery_status === 'pending'"
    :aria-live="message.source === 'voice' ? 'off' : undefined"
  >
    <p class="message-role">
      {{ message.role === 'assistant' ? 'Cornerstone' : 'You' }}
      <span v-if="message.source === 'voice'" class="message-source">Live</span>
    </p>
    <p class="message-content">
      {{ message.content }}<span
        v-if="message.transcript_status === 'streaming'"
        class="streaming-indicator"
        aria-hidden="true"
      ><span></span><span></span><span></span></span>
    </p>
    <span v-if="message.transcript_status === 'streaming'" class="visually-hidden">
      Speech in progress
    </span>
    <small v-if="message.delivery_status !== 'delivered'">
      {{
        message.delivery_status === 'pending'
          ? 'Sending…'
          : message.delivery_status === 'fallback'
            ? 'Saved fallback'
            : 'Delivery failed'
      }}
    </small>
  </article>
</template>

<style scoped>
.chat-message {
  display: grid;
  max-width: min(78%, 34rem);
  justify-self: start;
  gap: 0.25rem;
  padding: 0.7rem 0.9rem;
  border-radius: 1.1rem 1.1rem 1.1rem 0.3rem;
  color: var(--color-primary-strong);
  background: var(--color-secondary-soft);
  box-shadow: 0 0.25rem 0.8rem rgba(54, 85, 69, 0.08);
  overflow-wrap: anywhere;
}

.chat-message-user {
  justify-self: end;
  border-radius: 1.1rem 1.1rem 0.3rem 1.1rem;
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
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.message-source {
  margin-left: 0.35rem;
  opacity: 0.72;
}

.message-content {
  white-space: pre-wrap;
}

.streaming-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.15rem;
  margin-left: 0.35rem;
  vertical-align: middle;
}

.streaming-indicator span {
  width: 0.24rem;
  height: 0.24rem;
  border-radius: 50%;
  background: currentcolor;
  animation: transcript-pulse 1.2s ease-in-out infinite;
}

.streaming-indicator span:nth-child(2) {
  animation-delay: 0.16s;
}

.streaming-indicator span:nth-child(3) {
  animation-delay: 0.32s;
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

@keyframes transcript-pulse {
  0%,
  60%,
  100% {
    opacity: 0.35;
    transform: translateY(0);
  }

  30% {
    opacity: 1;
    transform: translateY(-0.12rem);
  }
}

@media (prefers-reduced-motion: reduce) {
  .streaming-indicator span {
    animation: none;
    opacity: 0.75;
  }
}

small {
  font-weight: 700;
}

@media (max-width: 34rem) {
  .chat-message {
    max-width: 86%;
  }
}
</style>
