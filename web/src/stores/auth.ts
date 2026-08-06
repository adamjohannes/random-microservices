import { defineStore } from 'pinia'
import { ref } from 'vue'
import { accountApi } from '@/api/account'
import { courseApi } from '@/api/course'
import type { Account } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const account = ref<Account | null>(null)

  async function _syncToServices(acc: Account, tok: string) {
    localStorage.setItem('access_token', tok)
    token.value = tok
    account.value = acc
    try {
      await courseApi.syncUser(acc.id, acc.name, acc.email)
    } catch {
      // non-fatal: course sync failure should not block login
    }
  }

  async function login(email: string, password: string) {
    const { data } = await accountApi.login(email, password)
    await _syncToServices(data.account, data.access_token)
  }

  async function register(email: string, password: string, name: string) {
    await accountApi.register(email, password, name)
    const { data } = await accountApi.login(email, password)
    await _syncToServices(data.account, data.access_token)
  }

  async function fetchAccount() {
    if (!account.value && token.value) {
      // decode sub from JWT to get id
      try {
        const payload = JSON.parse(atob(token.value.split('.')[1] ?? ''))
        const { data } = await accountApi.getAccount(payload.sub)
        account.value = data
      } catch {
        logout()
      }
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    token.value = null
    account.value = null
  }

  return { token, account, login, register, logout, fetchAccount }
})
