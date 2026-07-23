import re
from dataclasses import dataclass

from src.course.domain.exceptions import EmptyEmailError, InvalidEmailFormatError

EMAIL_REGEX = re.compile(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$")


@dataclass(frozen=True)
class UserEmail:
    """
    A validated, immutable email address.

    The value is stripped and lowercased, must be non-empty, and must match
    the expected email format.

    Raises:
        EmptyEmailError: If the value is empty.
        InvalidEmailFormatError: If the value is not a valid email.
    """
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
