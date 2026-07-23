from dataclasses import dataclass

from src.course.domain.exceptions import InvalidTitleLength


@dataclass(frozen=True)
class Title:
    """
    A validated, immutable title.

    The value is stripped of surrounding whitespace and must be 3-100
    characters long.

    Raises:
        InvalidTitleLength: If the value is empty, too short, or too long.
    """
    value: str

    def __post_init__(self) -> None:
        clean_value = self.value.strip() if isinstance(self.value, str) else self.value
        object.__setattr__(self, "value", clean_value)

        if not self.value:
            raise InvalidTitleLength("title cannot be empty or just whitespace")

        if len(self.value) < 3:
            raise InvalidTitleLength("title must be at least 3 characters long")

        if len(self.value) > 100:
            raise InvalidTitleLength("title cannot exceed 100 characters")

    def __str__(self) -> str:
        return self.value
