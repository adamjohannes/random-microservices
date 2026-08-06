<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { accountApi } from '@/api/account'
import ErrorAlert from '@/components/shared/ErrorAlert.vue'
import ConfirmDialog from '@/components/shared/ConfirmDialog.vue'

const auth = useAuthStore()
const router = useRouter()

const editName = ref(auth.account?.name ?? '')
const editEmail = ref(auth.account?.email ?? '')
const oldPassword = ref('')
const newPassword = ref('')
const profileError = ref<string | null>(null)
const passwordError = ref<string | null>(null)
const profileSuccess = ref(false)
const passwordSuccess = ref(false)
const showDeleteDialog = ref(false)

async function saveProfile() {
  profileError.value = null
  profileSuccess.value = false
  try {
    await accountApi.updateAccount(auth.account!.id, editName.value, editEmail.value)
    await auth.fetchAccount()
    profileSuccess.value = true
  } catch (e: any) {
    profileError.value = e.response?.data?.error ?? 'Update failed'
  }
}

async function changePassword() {
  passwordError.value = null
  passwordSuccess.value = false
  try {
    await accountApi.changePassword(auth.account!.id, oldPassword.value, newPassword.value)
    oldPassword.value = ''
    newPassword.value = ''
    passwordSuccess.value = true
  } catch (e: any) {
    passwordError.value = e.response?.data?.error ?? 'Password change failed'
  }
}

async function deleteAccount() {
  await accountApi.deleteAccount(auth.account!.id)
  auth.logout()
  router.push('/login')
}

onMounted(() => {
  editName.value = auth.account?.name ?? ''
  editEmail.value = auth.account?.email ?? ''
})
</script>

<template>
  <div class="max-w-lg mx-auto space-y-8">
    <h1 class="text-2xl font-bold">Profile</h1>

    <div class="bg-white rounded-xl shadow p-6 space-y-4">
      <h2 class="font-semibold text-lg">Account details</h2>
      <ErrorAlert v-if="profileError" :message="profileError" />
      <div v-if="profileSuccess" class="text-green-600 text-sm">Saved.</div>
      <form @submit.prevent="saveProfile" class="space-y-3">
        <div>
          <label class="block text-sm font-medium mb-1">Name</label>
          <input v-model="editName" type="text" required class="w-full border rounded-lg px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input v-model="editEmail" type="email" required class="w-full border rounded-lg px-3 py-2" />
        </div>
        <button type="submit" class="bg-blue-600 text-white rounded-lg px-4 py-2 font-semibold hover:bg-blue-700">Save</button>
      </form>
    </div>

    <div class="bg-white rounded-xl shadow p-6 space-y-4">
      <h2 class="font-semibold text-lg">Change password</h2>
      <ErrorAlert v-if="passwordError" :message="passwordError" />
      <div v-if="passwordSuccess" class="text-green-600 text-sm">Password changed.</div>
      <form @submit.prevent="changePassword" class="space-y-3">
        <div>
          <label class="block text-sm font-medium mb-1">Current password</label>
          <input v-model="oldPassword" type="password" required class="w-full border rounded-lg px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">New password</label>
          <input v-model="newPassword" type="password" required class="w-full border rounded-lg px-3 py-2" />
        </div>
        <button type="submit" class="bg-blue-600 text-white rounded-lg px-4 py-2 font-semibold hover:bg-blue-700">Change</button>
      </form>
    </div>

    <div class="bg-white rounded-xl shadow p-6">
      <h2 class="font-semibold text-lg text-red-600 mb-2">Danger zone</h2>
      <button @click="showDeleteDialog = true" class="bg-red-600 text-white rounded-lg px-4 py-2 font-semibold hover:bg-red-700">Delete account</button>
      <ConfirmDialog v-if="showDeleteDialog" message="Permanently delete your account? This cannot be undone." @confirm="deleteAccount" @cancel="showDeleteDialog = false" />
    </div>
  </div>
</template>
