<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const mobileOpen = ref(false)

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="bg-white border-b px-4 py-3 flex items-center justify-between">
    <RouterLink to="/courses" class="text-lg font-bold text-blue-600">LMS</RouterLink>
    <nav class="hidden md:flex items-center gap-4 text-sm font-medium">
      <RouterLink to="/courses" class="text-gray-600 hover:text-blue-600">Courses</RouterLink>
      <RouterLink to="/connections" class="text-gray-600 hover:text-blue-600">Connections</RouterLink>
      <RouterLink to="/connections/courses" class="text-gray-600 hover:text-blue-600">Feed</RouterLink>
      <RouterLink to="/profile" class="text-gray-600 hover:text-blue-600">{{ auth.account?.name ?? 'Profile' }}</RouterLink>
      <button @click="logout" class="text-red-500 hover:text-red-700">Sign out</button>
    </nav>
    <button class="md:hidden" @click="mobileOpen = !mobileOpen">☰</button>
    <div v-if="mobileOpen" class="absolute top-12 left-0 right-0 bg-white border-b shadow z-10 flex flex-col p-4 gap-3 text-sm font-medium md:hidden">
      <RouterLink to="/courses" @click="mobileOpen = false">Courses</RouterLink>
      <RouterLink to="/connections" @click="mobileOpen = false">Connections</RouterLink>
      <RouterLink to="/connections/courses" @click="mobileOpen = false">Feed</RouterLink>
      <RouterLink to="/profile" @click="mobileOpen = false">Profile</RouterLink>
      <button @click="logout" class="text-left text-red-500">Sign out</button>
    </div>
  </header>
</template>
