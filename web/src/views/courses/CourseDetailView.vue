<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCoursesStore } from '@/stores/courses'
import { useAuthStore } from '@/stores/auth'
import { courseApi } from '@/api/course'
import ChapterList from '@/components/course/ChapterList.vue'
import ChapterEditor from '@/components/course/ChapterEditor.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'

const route = useRoute()
const store = useCoursesStore()
const auth = useAuthStore()
const courseId = route.params.id as string

const actionError = ref<string | null>(null)
const showAddChapter = ref(false)

const course = computed(() => store.currentCourse)
const isAuthor = computed(() => auth.account?.id === course.value?.author.id)
const isEnrolled = computed(() => course.value?.assignee_ids.includes(auth.account?.id ?? '') ?? false)

async function toggleArchive() {
  actionError.value = null
  try {
    if (course.value?.archived_at) await courseApi.unarchiveCourse(courseId)
    else await courseApi.archiveCourse(courseId)
    await store.fetchOne(courseId)
  } catch (e: any) {
    actionError.value = e.response?.data?.detail ?? 'Action failed'
  }
}

async function toggleEnroll() {
  actionError.value = null
  try {
    if (isEnrolled.value) await courseApi.unenrollUser(courseId, auth.account!.id)
    else await courseApi.enrollUser(courseId, auth.account!.id)
    await store.fetchOne(courseId)
  } catch (e: any) {
    actionError.value = e.response?.data?.detail ?? 'Enroll failed'
  }
}

onMounted(() => store.fetchOne(courseId))
</script>

<template>
  <div>
    <LoadingSpinner v-if="store.loading" />
    <ErrorAlert v-else-if="store.error" :message="store.error" />
    <div v-else-if="course">
      <div class="flex items-start justify-between mb-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <h1 class="text-2xl font-bold">{{ course.title }}</h1>
            <span v-if="course.archived_at" class="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">Archived</span>
          </div>
          <p class="text-gray-500 text-sm">By {{ course.author.name }}</p>
        </div>
        <div class="flex gap-2">
          <button v-if="isAuthor" @click="toggleArchive" class="text-sm border rounded-lg px-3 py-1.5 hover:bg-gray-50">
            {{ course.archived_at ? 'Unarchive' : 'Archive' }}
          </button>
          <button v-if="!isAuthor" @click="toggleEnroll"
            :class="['text-sm rounded-lg px-3 py-1.5 font-medium', isEnrolled ? 'border hover:bg-gray-50' : 'bg-blue-600 text-white hover:bg-blue-700']">
            {{ isEnrolled ? 'Unenroll' : 'Enroll' }}
          </button>
        </div>
      </div>

      <p class="text-gray-700 mb-6">{{ course.description }}</p>

      <ErrorAlert v-if="actionError" :message="actionError" class="mb-4" />

      <div class="flex items-center justify-between mb-3">
        <h2 class="text-lg font-semibold">Chapters</h2>
        <button v-if="isAuthor && !course.archived_at" @click="showAddChapter = !showAddChapter"
          class="text-sm bg-blue-600 text-white rounded-lg px-3 py-1.5 hover:bg-blue-700">
          + Add chapter
        </button>
      </div>

      <ChapterEditor v-if="showAddChapter" :course-id="courseId" @saved="store.fetchOne(courseId); showAddChapter = false" />
      <ChapterList :course="course" :is-author="isAuthor" @refresh="store.fetchOne(courseId)" />
    </div>
  </div>
</template>
