import { client } from './client'
import type { Connection, CourseEnrollment } from '@/types'

export const connectionsApi = {
  sendRequest: (addresseeId: string) =>
    client.post<Connection>('/api/connections/connections', { addresseeId }),

  acceptRequest: (connectionId: string) =>
    client.patch<Connection>(`/api/connections/connections/${connectionId}/accept`),

  rejectRequest: (connectionId: string) =>
    client.patch<Connection>(`/api/connections/connections/${connectionId}/reject`),

  listConnections: () =>
    client.get<Connection[]>('/api/connections/connections'),

  listConnectionsCourses: () =>
    client.get<CourseEnrollment[]>('/api/connections/connections/courses'),
}
