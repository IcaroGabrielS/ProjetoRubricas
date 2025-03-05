import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import CreateStoreView from '../views/CreateStoreView.vue'
import StoreDetailView from '../views/StoreDetailView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/stores/create',
    name: 'create-store',
    component: CreateStoreView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/stores/:id',
    name: 'store-detail',
    component: StoreDetailView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Proteção de rotas
router.beforeEach((to, from, next) => {
  const loggedInStr = localStorage.getItem('user')
  const isLoggedIn = loggedInStr !== null
  let isAdmin = false
  
  if (isLoggedIn) {
    const user = JSON.parse(loggedInStr)
    isAdmin = user.is_admin === true
  }
  
  if (to.matched.some(record => record.meta.requiresAuth) && !isLoggedIn) {
    next('/login')
  } else if (to.matched.some(record => record.meta.requiresAdmin) && !isAdmin) {
    next('/')
  } else {
    next()
  }
})

export default router