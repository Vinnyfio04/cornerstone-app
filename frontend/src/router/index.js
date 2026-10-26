import { createRouter, createWebHistory } from 'vue-router'

import AccountPage from '../pages/AccountPage.vue'
import ChatPage from '../pages/ChatPage.vue'
import CrisisSupportPage from '../pages/CrisisSupportPage.vue'
import GroundingPage from '../pages/GroundingPage.vue'
import HistoryPage from '../pages/HistoryPage.vue'
import HomePage from '../pages/HomePage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/grounding', name: 'grounding', component: GroundingPage },
    { path: '/chat', name: 'chat', component: ChatPage },
    { path: '/history', name: 'history', component: HistoryPage },
    { path: '/account', name: 'account', component: AccountPage },
    { path: '/support', name: 'support', component: CrisisSupportPage },
  ],
})

export default router
