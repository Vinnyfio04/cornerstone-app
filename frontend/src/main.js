import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createAccountSession, provideAccountSession } from './session/accountSession.js'

const app = createApp(App)
const accountSession = createAccountSession()

app.use(router)
provideAccountSession(app, accountSession)
accountSession.initialize().catch(() => {
  // The shell, breathing exercise, and support information remain available.
})
app.mount('#app')
