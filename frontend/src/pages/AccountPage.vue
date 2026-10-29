<script setup>
import { ref, watch } from 'vue'

import { useAccountSession } from '../session/accountSession.js'

const accountSession = useAccountSession()
const loginUsername = ref('')
const loginPassword = ref('')
const registrationUsername = ref('')
const registrationFirstName = ref('')
const registrationLastName = ref('')
const registrationPassword = ref('')
const authView = ref('sign-in')
const username = ref('')
const firstName = ref('')
const lastName = ref('')
const newPassword = ref('')
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

function beginRequest() {
  isSubmitting.value = true
  successMessage.value = ''
  errorMessage.value = ''
}

function showAuthView(view) {
  authView.value = view
  successMessage.value = ''
  errorMessage.value = ''
}

async function signIn() {
  if (isSubmitting.value) return
  beginRequest()
  try {
    await accountSession.login(loginUsername.value.trim(), loginPassword.value)
    loginPassword.value = ''
    successMessage.value = 'Signed in.'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

async function registerAccount() {
  if (isSubmitting.value) return
  beginRequest()
  try {
    await accountSession.register({
      username: registrationUsername.value.trim(),
      firstName: registrationFirstName.value.trim(),
      lastName: registrationLastName.value.trim(),
      password: registrationPassword.value,
    })
    registrationPassword.value = ''
    successMessage.value = 'Account created and signed in.'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

async function saveAccount() {
  if (isSubmitting.value) return
  beginRequest()
  try {
    const fields = {
      username: username.value.trim(),
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
    }
    if (newPassword.value) fields.password = newPassword.value
    await accountSession.updateAccount(fields)
    newPassword.value = ''
    successMessage.value = 'Account saved.'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

function logOut() {
  accountSession.logout()
  successMessage.value = 'Signed out. Breathing and support information remain available.'
  errorMessage.value = ''
}

async function deleteAccount() {
  if (
    isSubmitting.value ||
    !window.confirm('Delete this account and all of its saved conversations and exercises?')
  ) {
    return
  }
  beginRequest()
  try {
    await accountSession.deleteAccount()
    successMessage.value = 'Account and saved activity deleted.'
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

watch(
  () => accountSession.user.value,
  (account) => {
    username.value = account?.username ?? ''
    firstName.value = account?.first_name ?? ''
    lastName.value = account?.last_name ?? ''
  },
  { immediate: true },
)
</script>

<template>
  <main class="account-page" data-page="account">
    <header>
      <p class="eyebrow">Your local prototype account</p>
      <h1>Account</h1>
      <p>
        Sign in to save grounding, conversations, and history. Breathing and crisis-support
        information stay available while signed out.
      </p>
    </header>

    <p v-if="accountSession.isLoading.value" aria-live="polite">Checking your saved sign-in…</p>

    <section v-else-if="!accountSession.user.value" class="account-panel">
      <form v-if="authView === 'sign-in'" class="account-form" @submit.prevent="signIn">
        <h2>Sign in</h2>
        <label for="login-username">Username</label>
        <input
          id="login-username"
          v-model="loginUsername"
          minlength="3"
          maxlength="50"
          autocomplete="username"
          required
        />
        <label for="login-password">Password</label>
        <input
          id="login-password"
          v-model="loginPassword"
          type="password"
          minlength="8"
          maxlength="128"
          autocomplete="current-password"
          required
        />
        <div class="account-actions">
          <button type="submit" :disabled="isSubmitting">Sign in</button>
          <button
            type="button"
            class="secondary-button"
            :disabled="isSubmitting"
            @click="showAuthView('create-account')"
          >
            Create account
          </button>
        </div>
      </form>

      <form v-else class="account-form" @submit.prevent="registerAccount">
        <h2>Create account</h2>
        <label for="registration-username">Username</label>
        <input
          id="registration-username"
          v-model="registrationUsername"
          minlength="3"
          maxlength="50"
          pattern="[A-Za-z0-9._-]+"
          autocomplete="username"
          required
        />
        <small>Use letters, numbers, periods, underscores, or hyphens.</small>
        <label for="registration-first-name">First name</label>
        <input
          id="registration-first-name"
          v-model="registrationFirstName"
          maxlength="50"
          autocomplete="given-name"
          required
        />
        <label for="registration-last-name">Last name</label>
        <input
          id="registration-last-name"
          v-model="registrationLastName"
          maxlength="50"
          autocomplete="family-name"
          required
        />
        <label for="registration-password">Password</label>
        <input
          id="registration-password"
          v-model="registrationPassword"
          type="password"
          minlength="8"
          maxlength="128"
          autocomplete="new-password"
          required
        />
        <div class="account-actions">
          <button type="submit" :disabled="isSubmitting">Create account</button>
          <button
            type="button"
            class="secondary-button"
            :disabled="isSubmitting"
            @click="showAuthView('sign-in')"
          >
            Sign in
          </button>
        </div>
      </form>
    </section>

    <form v-else class="account-form" @submit.prevent="saveAccount">
      <h2>Profile</h2>
      <label for="account-username">Username</label>
      <input
        id="account-username"
        v-model="username"
        minlength="3"
        maxlength="50"
        pattern="[A-Za-z0-9._-]+"
        autocomplete="username"
        required
      />
      <label for="first-name">First name</label>
      <input
        id="first-name"
        v-model="firstName"
        maxlength="50"
        autocomplete="given-name"
        required
      />
      <label for="last-name">Last name</label>
      <input
        id="last-name"
        v-model="lastName"
        maxlength="50"
        autocomplete="family-name"
        required
      />
      <label for="new-password">New password <span>(optional)</span></label>
      <input
        id="new-password"
        v-model="newPassword"
        type="password"
        minlength="8"
        maxlength="128"
        autocomplete="new-password"
      />
      <p class="account-id">SQLite user identifier: {{ accountSession.user.value.id }}</p>
      <div class="account-actions">
        <button type="submit" :disabled="isSubmitting">Save account</button>
        <button type="button" class="secondary-button" :disabled="isSubmitting" @click="logOut">
          Log out
        </button>
        <button type="button" class="danger-button" :disabled="isSubmitting" @click="deleteAccount">
          Delete account
        </button>
      </div>
    </form>

    <p v-if="successMessage" class="success-message" role="status">{{ successMessage }}</p>
    <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>
  </main>
</template>

<style scoped>
.account-page {
  display: grid;
  width: min(100% - 2rem, 40rem);
  align-content: start;
  gap: 1.25rem;
  margin: 0 auto;
  padding: 2.5rem 0 3rem;
}

header,
.account-form {
  display: grid;
  gap: 0.65rem;
}

h1 {
  color: var(--color-heading);
  font-size: clamp(2rem, 7vw, 3rem);
  font-weight: 750;
}

h2 {
  font-weight: 700;
}

.eyebrow {
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 750;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.account-form {
  padding: 1.25rem;
  border: 1px solid var(--color-border);
  border-radius: 1rem;
  background: var(--color-background-soft);
  box-shadow: var(--shadow-soft);
}

label {
  font-weight: 700;
}

small,
label span {
  color: var(--color-text-soft);
  font-size: 0.85rem;
}

input {
  min-height: 3rem;
  padding: 0.65rem 0.8rem;
  border: 2px solid var(--color-border-hover);
  border-radius: 0.75rem;
  color: var(--color-text);
  background: var(--color-background-soft);
  font: inherit;
}

button {
  justify-self: start;
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

.account-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.secondary-button {
  color: var(--color-primary-strong);
  background: var(--color-background-soft);
}

.danger-button {
  border-color: var(--color-danger);
  color: var(--color-danger-strong);
  background: var(--color-danger-soft);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

input:focus-visible,
button:focus-visible {
  outline: 3px solid var(--color-accent);
  outline-offset: 3px;
}

.account-id {
  color: var(--color-text-soft);
  font-size: 0.85rem;
}

.success-message,
.error-message {
  padding: 0.85rem 1rem;
  border-radius: 0.75rem;
}

.success-message {
  color: var(--color-primary-strong);
  background: var(--color-primary-soft);
}

.error-message {
  color: var(--color-danger-strong);
  background: var(--color-danger-soft);
}

</style>
