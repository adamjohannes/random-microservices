import { client } from './client'
import type { Course, Chapter } from '@/types'

export const courseApi = {
  syncUser: (account_id: string, name: string, email: string) =>
    client.post('/api/course/users', { account_id, name, email }),

  listCourses: (limit = 10, offset = 0) =>
    client.get<Course[]>('/api/course/courses', { params: { limit, offset } }),

  listAuthored: () =>
    client.get<Course[]>('/api/course/courses/authored'),

  listEnrolled: () =>
    client.get<Course[]>('/api/course/courses/enrolled'),

  getCourse: (id: string) =>
    client.get<Course>(`/api/course/courses/${id}`),

  createCourse: (title: string, description: string) =>
    client.post<Course>('/api/course/courses', { title, description }),

  archiveCourse: (id: string) =>
    client.patch(`/api/course/courses/${id}/archive`),

  unarchiveCourse: (id: string) =>
    client.patch(`/api/course/courses/${id}/unarchive`),

  enrollUser: (courseId: string, userId: string) =>
    client.post(`/api/course/courses/${courseId}/enroll/${userId}`),

  unenrollUser: (courseId: string, userId: string) =>
    client.delete(`/api/course/courses/${courseId}/enroll/${userId}`),

  addChapter: (courseId: string, title: string, body: string) =>
    client.post<Chapter>(`/api/course/courses/${courseId}/chapters`, { title, body }),

  updateChapter: (courseId: string, chapterId: string, title: string, body: string) =>
    client.put(`/api/course/courses/${courseId}/chapters/${chapterId}`, { title, body }),

  archiveChapter: (courseId: string, chapterId: string) =>
    client.patch(`/api/course/courses/${courseId}/chapters/${chapterId}/archive`),

  unarchiveChapter: (courseId: string, chapterId: string) =>
    client.patch(`/api/course/courses/${courseId}/chapters/${chapterId}/unarchive`),
}
