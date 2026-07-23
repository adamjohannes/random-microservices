from dataclasses import dataclass

from src.course.domain.exceptions import DomainValidationError


class InvalidTitleError(DomainValidationError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass(frozen=True)
class Title:
    value: str

    def __post_init__(self) -> None:
        clean_value = self.value.strip() if isinstance(self.value, str) else self.value
        object.__setattr__(self, "value", clean_value)

        if not self.value:
            raise InvalidTitleError("title cannot be empty or just whitespace")

        if len(self.value) < 3:
            raise InvalidTitleError("title must be at least 3 characters long")

        if len(self.value) > 100:
            raise InvalidTitleError("title cannot exceed 100 characters")

    def __str__(self) -> str:
        return self.value
