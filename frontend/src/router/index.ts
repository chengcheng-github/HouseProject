import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/house/:id',
      name: 'HouseDetail',
      component: () => import('@/views/HouseDetail.vue'),
      meta: { requiresAuth: false },
      props: true
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('@/views/Profile.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/publish',
      name: 'PublishHouse',
      component: () => import('@/views/PublishHouse.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/my-houses',
      name: 'MyHouses',
      component: () => import('@/views/MyHouses.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/edit-house/:id',
      name: 'EditHouse',
      component: () => import('@/views/EditHouse.vue'),
      meta: { requiresAuth: true },
      props: true
    },
    {
      path: '/my-visits',
      name: 'MyVisits',
      component: () => import('@/views/MyVisits.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'AdminDashboard',
      component: () => import('@/views/admin/Dashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      // 404页面
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: { requiresAuth: false }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  
  // 初始化用户状态
  if (!userStore.isAuthenticated && localStorage.getItem('token')) {
    await userStore.init()
  }
  
  const requiresAuth = to.meta.requiresAuth
  const requiresAdmin = to.meta.requiresAdmin
  
  if (requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (requiresAdmin && !userStore.isAdmin) {
    next({ name: 'Home' })
  } else if (!requiresAuth && userStore.isAuthenticated && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router