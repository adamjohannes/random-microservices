from uuid import UUID

from src.course.application.ports.course_repository import CourseRepository
from src.course.application.ports.user_repository import UserRepository
from src.course.domain.course import Course
from src.course.domain.exceptions import UserNotFoundError, CourseNotFoundError


class CourseUseCase:
    """
    Orchestrates the course-related business transactions.
    Dependencies are injected via the constructor.
    """

    def __init__(self, course_repo: CourseRepository, user_repo: UserRepository) -> None:
        self._course_repo = course_repo
        self._user_repo = user_repo

    async def create_course(self, actor_id: UUID, title: str, description: str) -> Course:
        """
        Creates a new course.
        """
        author = await self._user_repo.get_by_id(actor_id)

        if not author:
            raise UserNotFoundError(str(actor_id))

        course = Course.create(author=author, title_str=title, description=description)
        await self._course_repo.save(course)
        return course

    async def retrieve_course(self, course_id: UUID) -> Course:
        """
        Retrieves a course by its ID.
        """
        course = await self._course_repo.get_by_id(course_id)

        if not course:
            raise CourseNotFoundError(str(course_id))

        return course
