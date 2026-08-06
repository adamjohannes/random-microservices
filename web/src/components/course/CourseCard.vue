<script setup lang="ts">
import type { Course } from '@/types'
defineProps<{ course: Course }>()
</script>

<template>
  <div :class="['bg-white rounded-xl shadow p-4 cursor-pointer hover:shadow-md transition', course.archived_at ? 'opacity-60' : '']">
    <div class="flex items-start justify-between mb-1">
      <h3 class="font-semibold text-base truncate">{{ course.title }}</h3>
      <span v-if="course.archived_at" class="text-xs bg-gray-200 text-gray-500 px-2 py-0.5 rounded-full shrink-0 ml-2">Archived</span>
    </div>
    <p class="text-gray-500 text-sm line-clamp-2 mb-3">{{ course.description }}</p>
    <div class="text-xs text-gray-400">By {{ course.author.name }} · {{ course.chapters.length }} chapters</div>
  </div>
</template>
