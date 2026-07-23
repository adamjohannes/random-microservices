from dataclasses import dataclass

from src.course.domain.exceptions import DomainValidationError


class InvalidCourseDescriptionLenght(DomainValidationError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass(frozen=True)
class CourseDescription:
    """
    A validated, immutable course description.

    The value is stripped of surrounding whitespace and must be 30-2000
    characters long.

    Raises:
        InvalidCourseDescriptionLenght: If the value is empty, too short, or too long.
    """
    value: str

    def __post_init__(self) -> None:
        clean_value = self.value.strip() if isinstance(self.value, str) else self.value
        object.__setattr__(self, "value", clean_value)

        if not self.value:
            raise InvalidCourseDescriptionLenght("course description cannot be empty or just whitespace")

        if len(self.value) < 30:
            raise InvalidCourseDescriptionLenght("course description be at least 30 characters long")

        if len(self.value) > 2000:
            raise InvalidCourseDescriptionLenght("course description cannot exceed 2000 characters")

    def __str__(self) -> str:
        return self.value
