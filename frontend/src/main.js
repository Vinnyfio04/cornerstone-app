import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createDemoUserSession, provideDemoUserSession } from './session/demoUser.js'

const app = createApp(App)
const demoUserSession = createDemoUserSession()

app.use(router)
provideDemoUserSession(app, demoUserSession)
app.mount('#app')

demoUserSession.initialize().catch(() => {
  // The shell and deterministic exercises remain available while retry is shown.
})
