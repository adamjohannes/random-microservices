export interface Account {
  id: string
  name: string
  email: string
  created_at: string
  updated_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  account: Account
}

export interface Chapter {
  id: string
  index: number
  title: string
  body: string
  created_at: string
  updated_at: string
  archived_at: string | null
}

export interface Course {
  id: string
  author: Account
  title: string
  description: string
  chapters: Chapter[]
  assignee_ids: string[]
  created_at: string
  updated_at: string
  archived_at: string | null
}

export interface ConnectionUser {
  id: string
  name: string
  email: string
}

export interface Connection {
  id: string
  status: 'PENDING' | 'ACCEPTED' | 'REJECTED'
  requester: ConnectionUser
  addressee: ConnectionUser
  createdAt: string
  updatedAt: string
}

export interface CourseEnrollment {
  courseId: string
  courseTitle: string
  enrolledUserId: string
  enrolledUserName: string
}
