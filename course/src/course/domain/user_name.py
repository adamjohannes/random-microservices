import re
from dataclasses import dataclass

from src.course.domain.exceptions import DomainValidationError

NAME_REGEX = re.compile(r"^[a-zA-Z\s]+$")

class InvalidNameLenghtError(DomainValidationError):
    def __init__(self, message: str = "name must be between 2 and 50 characters") -> None:
        super().__init__(message)

class InvalidNameCharacterError(DomainValidationError):
    def __init__(self, message: str = "name must contain only alphabetical characters") -> None:
        super().__init__(message)


@dataclass(frozen=True)
class UserName:
    value: str

    def __post_init__(self) -> None:
        clean_value = self.value.strip() if isinstance(self.value, str) else self.value
        object.__setattr__(self, "value", clean_value)

        if not (2 <= len(self.value) <= 50):
            raise InvalidNameLenghtError()

        if not NAME_REGEX.match(self.value):
            raise InvalidNameCharacterError()

    def __str__(self) -> str:
        return self.value
