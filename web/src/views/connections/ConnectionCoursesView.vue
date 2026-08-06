<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useConnectionsStore } from '@/stores/connections'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'
import type { CourseEnrollment } from '@/types'

const store = useConnectionsStore()

const byCourse = computed(() => {
  const map = new Map<string, { title: string; enrollees: CourseEnrollment[] }>()
  for (const e of store.connectionCourses) {
    if (!map.has(e.courseId)) map.set(e.courseId, { title: e.courseTitle, enrollees: [] })
    map.get(e.courseId)!.enrollees.push(e)
  }
  return [...map.values()]
})

onMounted(() => store.fetchConnectionCourses())
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">What my connections are learning</h1>
    <LoadingSpinner v-if="store.loading" />
    <ErrorAlert v-else-if="store.error" :message="store.error" />
    <div v-else-if="byCourse.length === 0" class="text-gray-400 text-center py-16">
      Your connections haven't enrolled in any courses yet.
    </div>
    <div v-else class="space-y-4">
      <div v-for="group in byCourse" :key="group.title" class="bg-white rounded-xl shadow p-5">
        <h2 class="font-semibold text-lg mb-2">{{ group.title }}</h2>
        <ul class="space-y-1">
          <li v-for="e in group.enrollees" :key="e.enrolledUserId" class="text-sm text-gray-600">
            {{ e.enrolledUserName }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
