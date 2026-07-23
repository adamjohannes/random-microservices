import re
from dataclasses import dataclass

from src.course.domain.exceptions import DomainValidationError

EMAIL_REGEX = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")


class EmptyEmailError(DomainValidationError):
    def __init__(self, message: str = "email cannot be empty") -> None:
        super().__init__(message)


class InvalidEmailFormatError(DomainValidationError):
    def __init__(self, message: str = "invalid email format") -> None:
        super().__init__(message)


@dataclass(frozen=True)
class UserEmail:
    value: str

    def __post_init__(self) -> None:
        clean_value = self.value.strip().lower() if isinstance(self.value, str) else self.value
        object.__setattr__(self, "value", clean_value)

        if not self.value:
            raise EmptyEmailError()

        if not EMAIL_REGEX.match(self.value):
            raise InvalidEmailFormatError()

    def __str__(self) -> str:
        return str(self.value)
