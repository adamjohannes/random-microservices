<script setup lang="ts">
import { ref } from 'vue'
import { courseApi } from '@/api/course'
import type { Course, Chapter } from '@/types'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'

const props = defineProps<{ course: Course; isAuthor: boolean }>()
const emit = defineEmits<{ refresh: [] }>()

const editing = ref<Chapter | null>(null)
const editTitle = ref('')
const editBody = ref('')
const error = ref<string | null>(null)

function startEdit(ch: Chapter) {
  editing.value = ch
  editTitle.value = ch.title
  editBody.value = ch.body
}

async function saveEdit() {
  if (!editing.value) return
  error.value = null
  try {
    await courseApi.updateChapter(props.course.id, editing.value.id, editTitle.value, editBody.value)
    editing.value = null
    emit('refresh')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Update failed'
  }
}

async function toggleArchiveChapter(ch: Chapter) {
  error.value = null
  try {
    if (ch.archived_at) await courseApi.unarchiveChapter(props.course.id, ch.id)
    else await courseApi.archiveChapter(props.course.id, ch.id)
    emit('refresh')
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Action failed'
  }
}

const sorted = () => [...props.course.chapters].sort((a, b) => a.index - b.index)
</script>

<template>
  <div>
    <ErrorAlert v-if="error" :message="error" class="mb-3" />
    <div v-if="sorted().length === 0" class="text-gray-400 text-sm py-4">No chapters yet.</div>
    <div v-for="ch in sorted()" :key="ch.id" :class="['bg-white rounded-xl shadow p-4 mb-3', ch.archived_at ? 'opacity-60' : '']">
      <template v-if="editing?.id === ch.id">
        <input v-model="editTitle" class="w-full border rounded px-2 py-1 mb-2 text-sm" />
        <textarea v-model="editBody" rows="4" class="w-full border rounded px-2 py-1 mb-2 text-sm"></textarea>
        <div class="flex gap-2">
          <button @click="saveEdit" class="bg-blue-600 text-white rounded px-3 py-1 text-sm">Save</button>
          <button @click="editing = null" class="border rounded px-3 py-1 text-sm">Cancel</button>
        </div>
      </template>
      <template v-else>
        <div class="flex items-start justify-between">
          <div>
            <span class="text-xs text-gray-400 mr-2">{{ ch.index + 1 }}.</span>
            <span class="font-medium">{{ ch.title }}</span>
            <span v-if="ch.archived_at" class="ml-2 text-xs bg-gray-200 text-gray-500 px-1.5 py-0.5 rounded-full">Archived</span>
          </div>
          <div v-if="isAuthor && !course.archived_at" class="flex gap-1 shrink-0 ml-2">
            <button @click="startEdit(ch)" class="text-xs border rounded px-2 py-0.5 hover:bg-gray-50">Edit</button>
            <button @click="toggleArchiveChapter(ch)" class="text-xs border rounded px-2 py-0.5 hover:bg-gray-50">
              {{ ch.archived_at ? 'Unarchive' : 'Archive' }}
            </button>
          </div>
        </div>
        <p class="mt-2 text-sm text-gray-600 whitespace-pre-wrap">{{ ch.body }}</p>
      </template>
    </div>
  </div>
</template>
