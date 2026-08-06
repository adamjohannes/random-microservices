import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { connectionsApi } from '@/api/connections'
import { useAuthStore } from './auth'
import type { Connection, CourseEnrollment } from '@/types'

export const useConnectionsStore = defineStore('connections', () => {
  const connections = ref<Connection[]>([])
  const connectionCourses = ref<CourseEnrollment[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const pendingReceived = computed(() => {
    const auth = useAuthStore()
    return connections.value.filter(
      (c) => c.status === 'PENDING' && c.addressee.id === auth.account?.id,
    )
  })

  const accepted = computed(() =>
    connections.value.filter((c) => c.status === 'ACCEPTED'),
  )

  async function fetchConnections() {
    loading.value = true; error.value = null
    try {
      const { data } = await connectionsApi.listConnections()
      connections.value = data
    } catch (e: any) {
      error.value = e.response?.data?.detail ?? 'Failed to load connections'
    } finally { loading.value = false }
  }

  async function fetchConnectionCourses() {
    loading.value = true; error.value = null
    try {
      const { data } = await connectionsApi.listConnectionsCourses()
      connectionCourses.value = data
    } catch (e: any) {
      error.value = e.response?.data?.detail ?? 'Failed to load courses'
    } finally { loading.value = false }
  }

  return {
    connections, connectionCourses, loading, error,
    pendingReceived, accepted,
    fetchConnections, fetchConnectionCourses,
  }
})
