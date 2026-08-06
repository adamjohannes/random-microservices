<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')
const name = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = null
  try {
    await auth.register(email.value, password.value, name.value)
    router.push('/courses')
  } catch (e: any) {
    error.value = e.response?.data?.error ?? 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm bg-white rounded-xl shadow p-8">
      <h1 class="text-2xl font-bold mb-6 text-center">Create account</h1>
      <ErrorAlert v-if="error" :message="error" class="mb-4" />
      <form @submit.prevent="submit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Full name</label>
          <input v-model="name" type="text" required class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input v-model="email" type="email" required class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input v-model="password" type="password" required class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <button type="submit" :disabled="loading" class="w-full bg-blue-600 text-white rounded-lg py-2 font-semibold hover:bg-blue-700 disabled:opacity-50">
          {{ loading ? 'Creating account…' : 'Create account' }}
        </button>
      </form>
      <p class="mt-4 text-center text-sm text-gray-500">
        Already have an account? <RouterLink to="/login" class="text-blue-600 hover:underline">Sign in</RouterLink>
      </p>
    </div>
  </div>
</template>
