import { client } from './client'
import type { Account, LoginResponse } from '@/types'

export const accountApi = {
  register: (email: string, password: string, name: string) =>
    client.post<Account>('/api/account/', { email, password, name }),

  login: (email: string, password: string) =>
    client.post<LoginResponse>('/api/account/login', { email, password }),

  getAccount: (id: string) =>
    client.get<Account>(`/api/account/${id}`),

  updateAccount: (id: string, name: string, email: string) =>
    client.put(`/api/account/${id}`, { name, email }),

  changePassword: (id: string, old_password: string, new_password: string) =>
    client.patch(`/api/account/${id}/password`, { old_password, new_password }),

  deleteAccount: (id: string) =>
    client.delete(`/api/account/${id}`),
}
