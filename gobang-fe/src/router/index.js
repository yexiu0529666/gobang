import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/leaderboard',
      name: 'leaderboard',
      component: () => import('@/views/LeaderboardView.vue')
    },
    {
      path: '/new-game',
      name: 'new-game',
      component: () => import('@/views/game/NewGameView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/game/:id',
      name: 'game',
      component: () => import('@/views/game/GameView.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/replays',
      name: 'replays',
      component: () => import('@/views/replay/ReplayListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/replay/:id',
      name: 'replay',
      component: () => import('@/views/replay/ReplayView.vue'),
      meta: { requiresAuth: true },
      props: true
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router 