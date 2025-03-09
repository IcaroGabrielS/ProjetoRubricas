import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import CreateGroupView from '../views/CreateGroupView.vue'
import GroupDetailView from '../views/GroupDetailView.vue'
import UsersView from '../views/UsersView.vue'
import GroupManageView from '../views/GroupManageView.vue'
import CompanyDetailView from '../views/CompanyDetailView.vue'

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
    component: LoginView,
    meta: { redirectIfLoggedIn: true }
  },
  {
    path: '/groups/create',
    name: 'create-group',
    component: CreateGroupView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/groups/:name',
    name: 'group-detail',
    component: GroupDetailView,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'users',
    component: UsersView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/groups/manage/:id',
    name: 'group-manage',
    component: GroupManageView,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/companies/:id',
    name: 'company-detail',
    component: CompanyDetailView,
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
  
  // Redirect to home if user is already logged in and tries to access login page
  if (to.matched.some(record => record.meta.redirectIfLoggedIn) && isLoggedIn) {
    next('/')
    return
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