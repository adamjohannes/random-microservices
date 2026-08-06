import { defineStore } from 'pinia'
import { ref } from 'vue'
import { courseApi } from '@/api/course'
import type { Course } from '@/types'

export const useCoursesStore = defineStore('courses', () => {
  const courses = ref<Course[]>([])
  const currentCourse = ref<Course | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll(limit = 10, offset = 0) {
    loading.value = true; error.value = null
    try {
      const { data } = await courseApi.listCourses(limit, offset)
      courses.value = data
    } catch (e: any) {
      error.value = e.response?.data?.detail ?? 'Failed to load courses'
    } finally { loading.value = false }
  }

  async function fetchAuthored() {
    loading.value = true; error.value = null
    try {
      const { data } = await courseApi.listAuthored()
      courses.value = data
    } catch (e: any) {
      error.value = e.response?.data?.detail ?? 'Failed to load courses'
    } finally { loading.value = false }
  }

  async function fetchEnrolled() {
    loading.value = true; error.value = null
    try {
      const { data } = await courseApi.listEnrolled()
      courses.value = data
    } catch (e: any) {
      error.value = e.response?.data?.detail ?? 'Failed to load courses'
    } finally { loading.value = false }
  }

  async function fetchOne(id: string) {
    loading.value = true; error.value = null
    try {
      const { data } = await courseApi.getCourse(id)
      currentCourse.value = data
    } catch (e: any) {
      error.value = e.response?.data?.detail ?? 'Failed to load course'
    } finally { loading.value = false }
  }

  return { courses, currentCourse, loading, error, fetchAll, fetchAuthored, fetchEnrolled, fetchOne }
})
