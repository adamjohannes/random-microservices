<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCoursesStore } from '@/stores/courses'
import { useRouter } from 'vue-router'
import CourseCard from '@/components/course/CourseCard.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'

const store = useCoursesStore()
const router = useRouter()
const tab = ref<'all' | 'authored' | 'enrolled'>('all')

async function loadTab(t: typeof tab.value) {
  tab.value = t
  if (t === 'all') await store.fetchAll()
  else if (t === 'authored') await store.fetchAuthored()
  else await store.fetchEnrolled()
}

onMounted(() => loadTab('all'))
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Courses</h1>
      <RouterLink to="/courses/new" class="bg-blue-600 text-white rounded-lg px-4 py-2 font-semibold hover:bg-blue-700 text-sm">+ New course</RouterLink>
    </div>

    <div class="flex gap-2 mb-6">
      <button v-for="t in (['all', 'authored', 'enrolled'] as const)" :key="t"
        @click="loadTab(t)"
        :class="['px-4 py-1.5 rounded-full text-sm font-medium transition', tab === t ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']">
        {{ t.charAt(0).toUpperCase() + t.slice(1) }}
      </button>
    </div>

    <LoadingSpinner v-if="store.loading" />
    <ErrorAlert v-else-if="store.error" :message="store.error" />
    <div v-else-if="store.courses.length === 0" class="text-gray-400 text-center py-16">No courses yet.</div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <CourseCard v-for="c in store.courses" :key="c.id" :course="c" @click="router.push(`/courses/${c.id}`)" />
    </div>
  </div>
</template>
