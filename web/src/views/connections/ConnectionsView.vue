<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useConnectionsStore } from '@/stores/connections'
import { useAuthStore } from '@/stores/auth'
import { connectionsApi } from '@/api/connections'
import UserCard from '@/components/connection/UserCard.vue'
import ConnectionStatus from '@/components/connection/ConnectionStatus.vue'
import LoadingSpinner from '@/components/shared/LoadingSpinner.vue'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'

const store = useConnectionsStore()
const auth = useAuthStore()
const addresseeId = ref('')
const sendError = ref<string | null>(null)
const sendLoading = ref(false)

async function sendRequest() {
  sendError.value = null
  sendLoading.value = true
  try {
    await connectionsApi.sendRequest(addresseeId.value.trim())
    addresseeId.value = ''
    await store.fetchConnections()
  } catch (e: any) {
    sendError.value = e.response?.data?.detail ?? e.response?.data?.message ?? 'Failed to send request'
  } finally {
    sendLoading.value = false }
}

async function accept(id: string) {
  await connectionsApi.acceptRequest(id)
  await store.fetchConnections()
}

async function reject(id: string) {
  await connectionsApi.rejectRequest(id)
  await store.fetchConnections()
}

onMounted(() => store.fetchConnections())
</script>

<template>
  <div class="space-y-8">
    <h1 class="text-2xl font-bold">Connections</h1>

    <div class="bg-white rounded-xl shadow p-6">
      <h2 class="font-semibold mb-3">Send connection request</h2>
      <ErrorAlert v-if="sendError" :message="sendError" class="mb-3" />
      <form @submit.prevent="sendRequest" class="flex gap-2">
        <input v-model="addresseeId" placeholder="User UUID" required class="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <button type="submit" :disabled="sendLoading" class="bg-blue-600 text-white rounded-lg px-4 py-2 text-sm font-semibold hover:bg-blue-700 disabled:opacity-50">
          {{ sendLoading ? '…' : 'Send' }}
        </button>
      </form>
    </div>

    <LoadingSpinner v-if="store.loading" />
    <ErrorAlert v-else-if="store.error" :message="store.error" />
    <template v-else>
      <div v-if="store.pendingReceived.length">
        <h2 class="font-semibold mb-3">Pending requests</h2>
        <div class="space-y-3">
          <div v-for="c in store.pendingReceived" :key="c.id" class="bg-white rounded-xl shadow p-4 flex items-center justify-between">
            <UserCard :user="c.requester" />
            <div class="flex gap-2">
              <button @click="accept(c.id)" class="bg-green-600 text-white rounded-lg px-3 py-1.5 text-sm font-medium hover:bg-green-700">Accept</button>
              <button @click="reject(c.id)" class="border rounded-lg px-3 py-1.5 text-sm font-medium hover:bg-gray-50">Reject</button>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h2 class="font-semibold mb-3">My connections</h2>
        <div v-if="store.accepted.length === 0" class="text-gray-400 text-center py-8">No connections yet.</div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div v-for="c in store.accepted" :key="c.id" class="bg-white rounded-xl shadow p-4">
            <UserCard :user="c.requester.id === auth.account?.id ? c.addressee : c.requester" />
            <ConnectionStatus :status="c.status" class="mt-2" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
