<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { courseApi } from '@/api/course'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'

const router = useRouter()
const title = ref('')
const description = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = null
  try {
    const { data } = await courseApi.createCourse(title.value, description.value)
    router.push(`/courses/${data.id}`)
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Failed to create course'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">New course</h1>
    <ErrorAlert v-if="error" :message="error" class="mb-4" />
    <form @submit.prevent="submit" class="bg-white rounded-xl shadow p-6 space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1">Title</label>
        <input v-model="title" type="text" required class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">Description</label>
        <textarea v-model="description" required rows="5" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
      </div>
      <div class="flex gap-3">
        <button type="submit" :disabled="loading" class="bg-blue-600 text-white rounded-lg px-4 py-2 font-semibold hover:bg-blue-700 disabled:opacity-50">
          {{ loading ? 'Creating…' : 'Create' }}
        </button>
        <RouterLink to="/courses" class="px-4 py-2 rounded-lg border hover:bg-gray-50 text-sm font-medium">Cancel</RouterLink>
      </div>
    </form>
  </div>
</template>
