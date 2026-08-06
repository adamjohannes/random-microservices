import pytest

from src.course.domain.exceptions import (
    EmptyEmailError,
    InvalidChapterBodyLength,
    InvalidCourseDescriptionLenght,
    InvalidEmailFormatError,
    InvalidNameCharacterError,
    InvalidNameLenghtError,
    InvalidTitleLength,
)
from src.course.domain.chapter_body import ChapterBody
from src.course.domain.course_description import CourseDescription
from src.course.domain.title import Title
from src.course.domain.user_email import UserEmail
from src.course.domain.user_name import UserName


class TestTitle:
    def test_valid(self) -> None:
        assert str(Title("Valid Title")) == "Valid Title"

    def test_strips_whitespace(self) -> None:
        assert str(Title("  Hello  ")) == "Hello"

    def test_too_short(self) -> None:
        with pytest.raises(InvalidTitleLength):
            Title("AB")

    def test_too_long(self) -> None:
        with pytest.raises(InvalidTitleLength):
            Title("A" * 101)

    def test_empty(self) -> None:
        with pytest.raises(InvalidTitleLength):
            Title("   ")


class TestCourseDescription:
    def test_valid(self) -> None:
        assert str(CourseDescription("A" * 30)) == "A" * 30

    def test_too_short(self) -> None:
        with pytest.raises(InvalidCourseDescriptionLenght):
            CourseDescription("A" * 29)

    def test_too_long(self) -> None:
        with pytest.raises(InvalidCourseDescriptionLenght):
            CourseDescription("A" * 2001)


class TestChapterBody:
    def test_valid(self) -> None:
        assert str(ChapterBody("B" * 30)) == "B" * 30

    def test_too_short(self) -> None:
        with pytest.raises(InvalidChapterBodyLength):
            ChapterBody("B" * 29)

    def test_too_long(self) -> None:
        with pytest.raises(InvalidChapterBodyLength):
            ChapterBody("B" * 10001)


class TestUserName:
    def test_valid(self) -> None:
        assert str(UserName("Adam Johannes")) == "Adam Johannes"

    def test_too_short(self) -> None:
        with pytest.raises(InvalidNameLenghtError):
            UserName("A")

    def test_too_long(self) -> None:
        with pytest.raises(InvalidNameLenghtError):
            UserName("A" * 51)

    def test_rejects_digits(self) -> None:
        with pytest.raises(InvalidNameCharacterError):
            UserName("Adam123")


class TestUserEmail:
    def test_valid(self) -> None:
        assert str(UserEmail("Adam@Example.COM")) == "adam@example.com"

    def test_empty(self) -> None:
        with pytest.raises(EmptyEmailError):
            UserEmail("   ")

    def test_invalid_format(self) -> None:
        with pytest.raises(InvalidEmailFormatError):
            UserEmail("not-an-email")
