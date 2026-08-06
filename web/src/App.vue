<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import AppHeader from '@/components/layout/AppHeader.vue'

const auth = useAuthStore()
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <AppHeader v-if="auth.token" />
    <main class="flex-1 max-w-5xl w-full mx-auto px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
