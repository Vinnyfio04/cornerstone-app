<template>
  <main class="page-shell support-page" data-page="support">
    <header class="support-header">
      <p class="eyebrow">United States · Pennsylvania</p>
      <h1>Crisis support information</h1>
    </header>
    <section class="support-card emergency-card" aria-labelledby="emergency-heading">
      <h2 id="emergency-heading">Immediate danger or a medical emergency</h2>
      <p>Call <a href="tel:911">911</a> or go to the nearest emergency department.</p>
    </section>
    <section class="support-card lifeline-card" aria-labelledby="lifeline-heading">
      <h2 id="lifeline-heading">988 Suicide &amp; Crisis Lifeline</h2>
      <p>For suicidal crisis or emotional distress in the United States:</p>
      <ul class="support-actions">
        <li>
          <a class="resource-button" href="tel:988?oai_link_source=model_response_hotline">
            Call 988
          </a>
        </li>
        <li>
          <a
            class="resource-button secondary-button"
            href="sms:988?oai_link_source=model_response_hotline"
          >
            Text 988
          </a>
        </li>
        <li>
          <a
            class="resource-button secondary-button"
            href="https://988lifeline.org/chat/?oai_link_source=model_response_hotline"
          >
            Chat online
          </a>
        </li>
      </ul>
    </section>
    <aside class="prototype-note">
      <p>
        Cornerstone is a coursework prototype. It cannot monitor you, contact a service for you,
        or provide emergency care. These links open external services; phone and internet access
        depend on your device and connection.
      </p>
    </aside>
    <footer class="support-sources">
      <p class="source-label">Sources reviewed November 2, 2026</p>
      <p>
        <a href="https://www.pa.gov/agencies/dhs/resources/mental-health-substance-use-disorder/988">
          Pennsylvania Department of Human Services
        </a>
        and
        <a href="https://www.samhsa.gov/find-support/in-crisis">SAMHSA crisis information</a>.
      </p>
    </footer>
  </main>
</template>

<style scoped>
.support-page {
  align-content: start;
  gap: 1.25rem;
}

.support-header,
.support-card {
  display: grid;
  gap: 0.65rem;
}

.support-header h1 {
  font-size: clamp(2rem, 5vw, 3rem);
}

.eyebrow {
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 750;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.support-card {
  min-width: 0;
  padding: 1.35rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: var(--color-background-soft);
  box-shadow: var(--shadow-soft);
}

h2 {
  color: var(--color-heading);
  font-size: 1.2rem;
  font-weight: 750;
  line-height: 1.4;
}

.emergency-card {
  border-color: var(--color-danger);
  background: linear-gradient(135deg, var(--color-background-soft), var(--color-danger-soft));
}

.emergency-card h2,
.emergency-card a {
  color: var(--color-danger-strong);
}

.lifeline-card {
  border-color: var(--color-border-hover);
  background: linear-gradient(135deg, var(--color-background-soft), var(--color-primary-soft));
}

.support-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
  margin: 0.4rem 0 0;
  padding: 0;
  list-style: none;
}

.resource-button {
  display: flex;
  min-height: 2.85rem;
  align-items: center;
  justify-content: center;
  padding: 0.55rem 0.9rem;
  border: 2px solid var(--color-primary);
  border-radius: 999px;
  color: var(--color-on-primary);
  background: var(--color-primary);
  font-weight: 700;
  text-align: center;
  text-decoration: none;
}

.secondary-button {
  color: var(--color-primary-strong);
  background: var(--color-background-soft);
}

.prototype-note {
  padding: 1rem 1.15rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  color: var(--color-text-soft);
  background: var(--color-background-soft);
  font-size: 0.9rem;
}

.support-sources {
  display: grid;
  gap: 0.3rem;
  padding-inline: 0.15rem;
  color: var(--color-text-soft);
  font-size: 0.8rem;
}

.source-label {
  font-weight: 700;
}

a {
  color: var(--color-primary-strong);
  overflow-wrap: anywhere;
  text-underline-offset: 0.2em;
}

a:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

@media (max-width: 34rem) {
  .support-card {
    padding: 1.1rem;
  }

  .support-actions {
    grid-template-columns: 1fr;
  }
}
</style>
