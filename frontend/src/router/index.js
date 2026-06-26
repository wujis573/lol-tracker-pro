import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/summoner/:puuid', name: 'profile', component: () => import('../views/ProfileView.vue') },
  { path: '/matches/:puuid', name: 'matches', component: () => import('../views/MatchListView.vue') },
  { path: '/match/:matchId', name: 'match-detail', component: () => import('../views/MatchDetailView.vue') },
  { path: '/leaderboard', name: 'leaderboard', component: () => import('../views/LeaderboardView.vue') },
  { path: '/settings', name: 'settings', component: () => import('../views/SettingsView.vue') },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
