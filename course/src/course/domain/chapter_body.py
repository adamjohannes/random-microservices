from dataclasses import dataclass

from src.course.domain.exceptions import InvalidChapterBodyLength


@dataclass(frozen=True)
class ChapterBody:
    """
    A validated, immutable chapter body.

    The value is stripped of surrounding whitespace and must be 30-10000
    characters long.

    Raises:
        InvalidChapterBodyLength: If the value is empty, too short, or too long.
    """
    value: str

    def __post_init__(self) -> None:
        clean_value = self.value.strip() if isinstance(self.value, str) else self.value
        object.__setattr__(self, "value", clean_value)

        if not self.value:
            raise InvalidChapterBodyLength("chapter body cannot be empty or just whitespace")

        if len(self.value) < 30:
            raise InvalidChapterBodyLength("chapter body be at least 30 characters long")

        if len(self.value) > 10000:
            raise InvalidChapterBodyLength("chapter body cannot exceed 10000 characters")

    def __str__(self) -> str:
        return self.value
