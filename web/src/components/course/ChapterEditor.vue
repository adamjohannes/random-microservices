<script setup lang="ts">
import { ref } from 'vue'
import { courseApi } from '@/api/course'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'

const props = defineProps<{ courseId: string }>()
const emit = defineEmits<{ saved: [] }>()

const title = ref('')
const body = ref('')
const error = ref<string | null>(null)
const loading = ref(false)

async function submit() {
  loading.value = true
  error.value = null
  try {
    await courseApi.addChapter(props.courseId, title.value, body.value)
    title.value = ''
    body.value = ''
    emit('saved')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Failed to add chapter'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-gray-50 rounded-xl border p-4 mb-4">
    <h3 class="font-medium mb-3 text-sm">New chapter</h3>
    <ErrorAlert v-if="error" :message="error" class="mb-2" />
    <form @submit.prevent="submit" class="space-y-2">
      <input v-model="title" placeholder="Title" required class="w-full border rounded px-3 py-2 text-sm" />
      <textarea v-model="body" placeholder="Content" required rows="4" class="w-full border rounded px-3 py-2 text-sm"></textarea>
      <div class="flex gap-2">
        <button type="submit" :disabled="loading" class="bg-blue-600 text-white rounded px-3 py-1.5 text-sm font-medium disabled:opacity-50">
          {{ loading ? 'Saving…' : 'Add chapter' }}
        </button>
        <button type="button" @click="emit('saved')" class="border rounded px-3 py-1.5 text-sm">Cancel</button>
      </div>
    </form>
  </div>
</template>
