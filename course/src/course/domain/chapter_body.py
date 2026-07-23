from dataclasses import dataclass


class InvalidChapterBodyError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass(frozen=True)
class ChapterBody:
    value: str

    def __post_init__(self) -> None:
        clean_value = self.value.strip() if isinstance(self.value, str) else self.value
        object.__setattr__(self, "value", clean_value)

        if not self.value:
            raise InvalidChapterBodyError("chapter body cannot be empty or just whitespace")

        if len(self.value) < 30:
            raise InvalidChapterBodyError("chapter body be at least 30 characters long")

        if len(self.value) > 10000:
            raise InvalidChapterBodyError("title cannot exceed 10000 characters")

    def __str__(self) -> str:
        return self.value
