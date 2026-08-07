from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.course.application.ports.course_repository import CourseRepository
from src.course.application.ports.user_repository import UserRepository
from src.course.domain.course import Course
from src.course.domain.course_chapter import CourseChapter
from src.course.domain.user import User
from src.course.domain.title import Title
from src.course.domain.course_description import CourseDescription
from src.course.domain.chapter_body import ChapterBody
from src.course.domain.user_name import UserName
from src.course.domain.user_email import UserEmail
from src.course.adapters.driven.storage.postgres.models import UserModel, CourseModel, CourseChapterModel


class PostgresUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if not model:
            model = UserModel(id=user.id)
            self._session.add(model)

        # Translate Domain Value Objects back to primitive strings
        model.name = str(user.name)
        model.email = str(user.email)
        model.created_at = user.created_at
        model.updated_at = user.updated_at
        await self._session.flush()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        model = await self._session.get(UserModel, user_id)
        if not model:
            return None

        # Reconstitute the pure Domain entity
        return User(
            id=model.id,
            name=UserName(model.name),
            email=UserEmail(model.email),
            created_at=model.created_at,
            updated_at=model.updated_at
        )


class PostgresCourseRepository(CourseRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, course: Course) -> None:
        model = await self._session.get(CourseModel, course.id)
        is_new = model is None
        if is_new:
            model = CourseModel(id=course.id)
            self._session.add(model)

        model.author_id = course.author.id
        model.title = str(course.title)
        model.description = str(course.description)
        model.created_at = course.created_at
        model.updated_at = course.updated_at
        model.archived_at = course.archived_at

        # Upsert Chapters
        existing_chapters = {} if is_new else {c.id: c for c in await model.awaitable_attrs.chapters}
        new_chapter_models = []
        for chapter in course.chapters:
            c_model = existing_chapters.get(chapter.id, CourseChapterModel(id=chapter.id))
            c_model.course_id = course.id
            c_model.index = chapter.index
            c_model.title = str(chapter.title)
            c_model.body = str(chapter.body)
            c_model.created_at = chapter.created_at
            c_model.updated_at = chapter.updated_at
            c_model.archived_at = chapter.archived_at
            new_chapter_models.append(c_model)
        model.chapters = new_chapter_models

        # Update Assignees — load existing list async first to avoid sync lazy-load
        if not is_new:
            await model.awaitable_attrs.assignees
        if course.assignee_ids:
            assignees = await self._session.execute(
                select(UserModel).where(UserModel.id.in_(course.assignee_ids))
            )
            model.assignees = list(assignees.scalars().all())
        else:
            model.assignees = []

        await self._session.flush()

    async def get_by_id(self, course_id: UUID) -> Optional[Course]:
        # Using selectinload (configured on the model) ensures chapters and author load asynchronously
        result = await self._session.execute(select(CourseModel).where(CourseModel.id == course_id))
        model = result.scalar_one_or_none()

        if not model:
            return None

        return self._map_to_domain(model)

    async def get_all(self, limit: int = 10, offset: int = 0) -> List[Course]:
        result = await self._session.execute(select(CourseModel).limit(limit).offset(offset))
        return [self._map_to_domain(m) for m in result.scalars().all()]

    async def get_by_author_id(self, author_id: UUID) -> List[Course]:
        result = await self._session.execute(select(CourseModel).where(CourseModel.author_id == author_id))
        return [self._map_to_domain(m) for m in result.scalars().all()]

    async def get_by_assignee_id(self, assignee_id: UUID) -> List[Course]:
        # Filter by presence in the assignees list
        result = await self._session.execute(
            select(CourseModel).where(CourseModel.assignees.any(UserModel.id == assignee_id))
        )
        return [self._map_to_domain(m) for m in result.scalars().all()]

    def _map_to_domain(self, model: CourseModel) -> Course:
        # Reconstitute the User
        author = User(
            id=model.author.id,
            name=UserName(model.author.name),
            email=UserEmail(model.author.email),
            created_at=model.author.created_at,
            updated_at=model.author.updated_at
        )

        # Reconstitute Chapters
        chapters = [
            CourseChapter(
                id=c.id,
                index=c.index,
                title=Title(c.title),
                body=ChapterBody(c.body),
                created_at=c.created_at,
                updated_at=c.updated_at,
                archived_at=c.archived_at
            ) for c in model.chapters
        ]

        # Reconstitute Course Aggregate
        return Course(
            id=model.id,
            author=author,
            title=Title(model.title),
            description=CourseDescription(model.description),
            chapters=chapters,
            assignee_ids={a.id for a in model.assignees},
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at
        )
