from typing import List
from uuid import UUID

from src.course.application.ports.course_repository import CourseRepository
from src.course.application.ports.user_repository import UserRepository
from src.course.domain.course import Course
from src.course.domain.course_chapter import CourseChapter
from src.course.domain.exceptions import UserNotFoundError, CourseNotFoundError


class CourseUseCase:
    """
    Orchestrates the course-related business transactions.

    Each method loads the relevant aggregates through the injected
    repositories, delegates the business rules to the domain, and persists
    the result. Dependencies are injected via the constructor.
    """

    def __init__(self, course_repo: CourseRepository, user_repo: UserRepository) -> None:
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def create_course(self, actor_id: UUID, title: str, description: str) -> Course:
        """
        Create a new course owned by the acting user.

        Args:
            actor_id: The user creating and owning the course.
            title: Raw title text; validated by the domain.
            description: Raw description text; validated by the domain.

        Returns:
            The newly created course.

        Raises:
            UserNotFoundError: If no user exists for actor_id.
            InvalidTitleLength: If title fails Title validation.
            InvalidCourseDescriptionLenght: If description fails CourseDescription validation.
        """
        author = await self._user_repo.get_by_id(actor_id)

        if not author:
            raise UserNotFoundError(str(actor_id))

        course = Course.create(author=author, title_str=title, description=description)
        await self._course_repo.save(course)
        return course

    async def retrieve_course(self, course_id: UUID) -> Course:
        """
        Fetch a course by its id.

        Args:
            course_id: The id of the course to retrieve.

        Returns:
            The requested course.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
        """
        course = await self._course_repo.get_by_id(course_id)

        if not course:
            raise CourseNotFoundError(str(course_id))

        return course

    async def add_chapter_to_course(self, actor_id: UUID, course_id: UUID, title: str, body: str) -> CourseChapter:
        """
        Add a new chapter to an existing course.

        Args:
            actor_id: The user performing the action; must be the author.
            course_id: The id of the course to add the chapter to.
            title: Raw chapter title; validated by the domain.
            body: Raw chapter content; validated by the domain.

        Returns:
            The newly created chapter.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            NotCourseAuthorError: If actor_id is not the course author.
            ArchivedCourseError: If the course is archived.
            InvalidTitleLength: If title fails Title validation.
            InvalidChapterBodyLength: If body fails ChapterBody validation.
        """
        course = await self.retrieve_course(course_id)

        chapter = course.add_chapter(title=title, body=body, actor_id=actor_id)
        await self._course_repo.save(course)
        return chapter

    async def update_chapter(
            self, actor_id: UUID, course_id: UUID, chapter_id: UUID, title: str, body: str
    ) -> None:
        """
        Update the title and body of a chapter within a course.

        Args:
            actor_id: The user performing the action; must be the author.
            course_id: The id of the course the chapter belongs to.
            chapter_id: The id of the chapter to update.
            title: Raw chapter title; validated by the domain.
            body: Raw chapter content; validated by the domain.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            NotCourseAuthorError: If actor_id is not the course author.
            ArchivedCourseError: If the course is archived.
            ArchivedChapterError: If the target chapter is archived.
            ChapterNotFoundError: If no chapter with chapter_id exists in the course.
            InvalidTitleLength: If title fails Title validation.
            InvalidChapterBodyLength: If body fails ChapterBody validation.
        """
        course = await self.retrieve_course(course_id)

        course.update_chapter(actor_id=actor_id, chapter_id=chapter_id, title_str=title, body_str=body)
        await self._course_repo.save(course)

    async def archive_chapter(self, actor_id: UUID, course_id: UUID, chapter_id: UUID) -> None:
        """
        Archive a single chapter within a course.

        Args:
            actor_id: The user performing the action; must be the author.
            course_id: The id of the course the chapter belongs to.
            chapter_id: The id of the chapter to archive.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            NotCourseAuthorError: If actor_id is not the course author.
            ArchivedCourseError: If the course is archived.
            ChapterNotFoundError: If no chapter with chapter_id exists in the course.
            AlreadyArchivedError: If the target chapter is already archived.
        """
        course = await self.retrieve_course(course_id)

        course.archive_chapter(actor_id=actor_id, chapter_id=chapter_id)
        await self._course_repo.save(course)

    async def unarchive_chapter(self, actor_id: UUID, course_id: UUID, chapter_id: UUID) -> None:
        """
        Restore an archived chapter within a course to a modifiable state.

        Args:
            actor_id: The user performing the action; must be the author.
            course_id: The id of the course the chapter belongs to.
            chapter_id: The id of the chapter to unarchive.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            NotCourseAuthorError: If actor_id is not the course author.
            ArchivedCourseError: If the course is archived.
            ChapterNotFoundError: If no chapter with chapter_id exists in the course.
            NotArchivedError: If the target chapter is not currently archived.
        """
        course = await self.retrieve_course(course_id)

        course.unarchive_chapter(actor_id=actor_id, chapter_id=chapter_id)
        await self._course_repo.save(course)

    async def archive_course(self, actor_id: UUID, course_id: UUID) -> None:
        """
        Archive a course, making it read-only.

        Args:
            actor_id: The user performing the action; must be the author.
            course_id: The id of the course to archive.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            NotCourseAuthorError: If actor_id is not the course author.
            AlreadyArchivedError: If the course is already archived.
        """
        course = await self.retrieve_course(course_id)

        course.archive(actor_id=actor_id)
        await self._course_repo.save(course)

    async def unarchive_course(self, actor_id: UUID, course_id: UUID) -> None:
        """
        Restore an archived course to a modifiable state.

        Args:
            actor_id: The user performing the action; must be the author.
            course_id: The id of the course to unarchive.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            NotCourseAuthorError: If actor_id is not the course author.
            NotArchivedError: If the course is not currently archived.
        """
        course = await self.retrieve_course(course_id)

        course.unarchive(actor_id=actor_id)
        await self._course_repo.save(course)

    async def enroll_user_in_course(self, user_id: UUID, course_id: UUID) -> None:
        """
        Enroll a user as an assignee of a course.

        Args:
            user_id: The user to enroll; cannot be the course author.
            course_id: The id of the course to enroll the user in.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            UserNotFoundError: If no user exists for user_id.
            ArchivedCourseError: If the course is archived.
            AuthorCannotBeAssigneeError: If user_id is the course author.
        """
        course = await self.retrieve_course(course_id)

        user = await self._user_repo.get_by_id(user_id)

        if not user:
            raise UserNotFoundError(str(user_id))

        course.enroll_user(user_id=user_id)
        await self._course_repo.save(course)

    async def unenroll_user_from_course(self, user_id: UUID, course_id: UUID) -> None:
        """
        Remove a user from a course's assignees; a no-op if not enrolled.

        Args:
            user_id: The user to unenroll.
            course_id: The id of the course to unenroll the user from.

        Raises:
            CourseNotFoundError: If no course exists for course_id.
            ArchivedCourseError: If the course is archived.
        """
        course = await self.retrieve_course(course_id)

        course.unenroll_user(user_id=user_id)
        await self._course_repo.save(course)

    async def list_paginated_courses(self, limit: int = 10, offset: int = 0) -> List[Course]:
        """
        Retrieve a paginated list of all courses.

        Args:
            limit: The maximum number of courses to return.
            offset: The offset of the first page to return.

        Returns:
            A paginated list of all courses.
        """
        return await self._course_repo.get_all(limit=limit, offset=offset)

    async def list_authored_courses(self, author_id: UUID) -> List[Course]:
        """
        Retrieve all courses owned by a specific author.

        Args:
            author_id: The author to list courses from.

        Returns:
            A list of courses owned by a specific author.
        """
        return await self._course_repo.get_by_author_id(author_id)

    async def list_enrolled_courses(self, assignee_id: UUID) -> List[Course]:
        """
        Retrieve all courses enrolled by a specific user.

        Args:
             assignee_id: The assignee to list courses from.

        Returns:
            A list of courses enrolled by a specific user.
        """
        return await self._course_repo.get_by_assignee_id(assignee_id)
