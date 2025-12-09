import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { getCookie } from '../utils/cookie'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/gate',
      name: 'gate',
      component: () => import('@/views/gate/GatePage.vue'),
    },
    {
      path: '/logs',
      name: 'logs',
      component: () => import('@/views/log/LogPage.vue'),
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('@/views/user/UserListPage.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
    },
  ],
})

// 네비게이션 가드 - 로그인 체크 (Gate 페이지는 제외)
router.beforeEach((to, from, next) => {
  const apiKey = getCookie('api_key')
  
  // 로그인 페이지는 항상 접근 가능
  if (to.name === 'login') {
    next()
    return
  }
  
  // Gate 페이지는 api_key가 쿠키나 쿼리 파라미터에 있으면 접근 가능
  if (to.name === 'gate') {
    next()
    return
  }
  
  // 다른 페이지는 로그인 필요
  if (!apiKey) {
    next({ name: 'login' })
  } else {
    next()
  }
})

export default router
