<template>
  <nav aria-label="Primary navigation">
    <ul>
      <li><RouterLink to="/">Home</RouterLink></li>
      <li><RouterLink to="/grounding">Grounding</RouterLink></li>
      <li><RouterLink to="/chat">Chat</RouterLink></li>
      <li><RouterLink to="/calendar">Check-in</RouterLink></li>
      <li><RouterLink to="/history">History</RouterLink></li>
      <li><RouterLink to="/account">Account</RouterLink></li>
    </ul>
  </nav>
</template>

<style scoped>
nav {
  position: fixed;
  z-index: 100;
  right: max(0.75rem, env(safe-area-inset-right));
  bottom: max(0.75rem, env(safe-area-inset-bottom));
  left: max(0.75rem, env(safe-area-inset-left));
  overflow-x: auto;
  width: min(calc(100% - 1.5rem), 42rem);
  margin: 0 auto;
  border: 1px solid var(--color-border-hover);
  border-radius: 1.25rem;
  background: rgba(255, 250, 242, 0.94);
  box-shadow: 0 0.8rem 2.5rem rgba(54, 85, 69, 0.22);
  backdrop-filter: blur(14px);
}

ul {
  display: flex;
  width: max-content;
  min-width: 100%;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.4rem;
  list-style: none;
}

a {
  display: inline-flex;
  min-height: 2.75rem;
  align-items: center;
  padding: 0.45rem 0.72rem;
  border-radius: 999px;
  color: inherit;
  font-weight: 600;
  text-decoration: none;
}

a:hover,
a.router-link-active {
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
}

a:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 2px;
}

@media (max-width: 34rem) {
  ul {
    justify-content: flex-start;
  }

  a {
    padding-inline: 0.65rem;
    font-size: 0.82rem;
  }
}
</style>
