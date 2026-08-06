from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


# --- Requests ---

class SyncUserRequest(BaseModel):
    account_id: UUID
    name: str
    email: str


class CreateCourseRequest(BaseModel):
    title: str
    description: str


class AddChapterRequest(BaseModel):
    title: str
    body: str


class UpdateChapterRequest(BaseModel):
    title: str
    body: str


# --- Responses ---

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


class ChapterResponse(BaseModel):
    id: UUID
    index: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]


class CourseResponse(BaseModel):
    id: UUID
    author: UserResponse
    title: str
    description: str
    chapters: List[ChapterResponse]
    assignee_ids: List[UUID]
    created_at: datetime
    updated_at: datetime
    archived_at: Optional[datetime]
