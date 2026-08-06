from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.course.adapters.driving.http.auth import get_current_user_id
from src.course.adapters.driving.http.dependencies import get_course_usecase
from src.course.adapters.driving.http.schemas import (
    AddChapterRequest,
    ChapterResponse,
    CourseResponse,
    CreateCourseRequest,
    UpdateChapterRequest,
    UserResponse,
)
from src.course.application.use_cases.course_usecase import CourseUseCase
from src.course.domain.course import Course

router = APIRouter(prefix="/courses", tags=["courses"])


def _chapter_response(chapter) -> ChapterResponse:
    return ChapterResponse(
        id=chapter.id,
        index=chapter.index,
        title=str(chapter.title),
        body=str(chapter.body),
        created_at=chapter.created_at,
        updated_at=chapter.updated_at,
        archived_at=chapter.archived_at,
    )


def _course_response(course: Course) -> CourseResponse:
    return CourseResponse(
        id=course.id,
        author=UserResponse(
            id=course.author.id,
            name=str(course.author.name),
            email=str(course.author.email),
            created_at=course.author.created_at,
            updated_at=course.author.updated_at,
        ),
        title=str(course.title),
        description=str(course.description),
        chapters=[_chapter_response(c) for c in course.chapters],
        assignee_ids=list(course.assignee_ids),
        created_at=course.created_at,
        updated_at=course.updated_at,
        archived_at=course.archived_at,
    )


@router.get("", status_code=status.HTTP_200_OK, response_model=List[CourseResponse])
async def list_courses(
    limit: int = 10,
    offset: int = 0,
    _actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> List[CourseResponse]:
    courses = await usecase.list_paginated_courses(limit=limit, offset=offset)
    return [_course_response(c) for c in courses]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CourseResponse)
async def create_course(
    body: CreateCourseRequest,
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> CourseResponse:
    course = await usecase.create_course(
        actor_id=actor_id,
        title=body.title,
        description=body.description,
    )
    return _course_response(course)


@router.get("/authored", status_code=status.HTTP_200_OK, response_model=List[CourseResponse])
async def list_authored_courses(
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> List[CourseResponse]:
    courses = await usecase.list_authored_courses(author_id=actor_id)
    return [_course_response(c) for c in courses]


@router.get("/enrolled", status_code=status.HTTP_200_OK, response_model=List[CourseResponse])
async def list_enrolled_courses(
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> List[CourseResponse]:
    courses = await usecase.list_enrolled_courses(assignee_id=actor_id)
    return [_course_response(c) for c in courses]


@router.get("/{course_id}", status_code=status.HTTP_200_OK, response_model=CourseResponse)
async def get_course(
    course_id: UUID,
    _actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> CourseResponse:
    course = await usecase.retrieve_course(course_id=course_id)
    return _course_response(course)


@router.patch("/{course_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_course(
    course_id: UUID,
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> None:
    await usecase.archive_course(actor_id=actor_id, course_id=course_id)


@router.patch("/{course_id}/unarchive", status_code=status.HTTP_204_NO_CONTENT)
async def unarchive_course(
    course_id: UUID,
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> None:
    await usecase.unarchive_course(actor_id=actor_id, course_id=course_id)


@router.post("/{course_id}/enroll/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def enroll_user(
    course_id: UUID,
    user_id: UUID,
    _actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> None:
    await usecase.enroll_user_in_course(user_id=user_id, course_id=course_id)


@router.delete("/{course_id}/enroll/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_user(
    course_id: UUID,
    user_id: UUID,
    _actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> None:
    await usecase.unenroll_user_from_course(user_id=user_id, course_id=course_id)


@router.post("/{course_id}/chapters", status_code=status.HTTP_201_CREATED, response_model=ChapterResponse)
async def add_chapter(
    course_id: UUID,
    body: AddChapterRequest,
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> ChapterResponse:
    chapter = await usecase.add_chapter_to_course(
        actor_id=actor_id,
        course_id=course_id,
        title=body.title,
        body=body.body,
    )
    return _chapter_response(chapter)


@router.put("/{course_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_chapter(
    course_id: UUID,
    chapter_id: UUID,
    body: UpdateChapterRequest,
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> None:
    await usecase.update_chapter(
        actor_id=actor_id,
        course_id=course_id,
        chapter_id=chapter_id,
        title=body.title,
        body=body.body,
    )


@router.patch("/{course_id}/chapters/{chapter_id}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_chapter(
    course_id: UUID,
    chapter_id: UUID,
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> None:
    await usecase.archive_chapter(actor_id=actor_id, course_id=course_id, chapter_id=chapter_id)


@router.patch("/{course_id}/chapters/{chapter_id}/unarchive", status_code=status.HTTP_204_NO_CONTENT)
async def unarchive_chapter(
    course_id: UUID,
    chapter_id: UUID,
    actor_id: UUID = Depends(get_current_user_id),
    usecase: CourseUseCase = Depends(get_course_usecase),
) -> None:
    await usecase.unarchive_chapter(actor_id=actor_id, course_id=course_id, chapter_id=chapter_id)
