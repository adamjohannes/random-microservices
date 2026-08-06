import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/courses' },
    { path: '/login', component: () => import('@/views/auth/LoginView.vue'), meta: { guest: true } },
    { path: '/register', component: () => import('@/views/auth/RegisterView.vue'), meta: { guest: true } },
    { path: '/profile', component: () => import('@/views/account/ProfileView.vue'), meta: { auth: true } },
    { path: '/courses', component: () => import('@/views/courses/CourseListView.vue'), meta: { auth: true } },
    { path: '/courses/new', component: () => import('@/views/courses/CourseCreateView.vue'), meta: { auth: true } },
    { path: '/courses/:id', component: () => import('@/views/courses/CourseDetailView.vue'), meta: { auth: true } },
    { path: '/connections', component: () => import('@/views/connections/ConnectionsView.vue'), meta: { auth: true } },
    { path: '/connections/courses', component: () => import('@/views/connections/ConnectionCoursesView.vue'), meta: { auth: true } },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.token) return '/login'
  if (to.meta.guest && auth.token) return '/courses'
  if (to.meta.auth && auth.token && !auth.account) await auth.fetchAccount()
})

export default router
