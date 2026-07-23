class DomainError(Exception):
    """Root exception for all domain-related errors"""
    pass

class DomainValidationError(DomainError):
    """
    Raised when a Value Object fails validation.
    The delivery layer will map this to a 400 Bad Request.
    """
    pass

class ResourceStateError(DomainError):
    """
    Raised when trying to perform an invalid action on an entity's current state.
    The delivery layer will map this to a 409 Conflict.
    """
    pass

class DomainAuthorizationError(DomainError):
    """
    Raised when a user attempts an action they don't have permission for.
    The delivery layer will map this to a 403 Forbidden.
    """

class EntityNotFoundError(DomainError):
    """
    Raised when a requested entity cannot be found.
    The delivery layer will map this to a 404 Not Found.
    """
    pass

# ----------------------------------------------------------------------------------------------------------------------

# --- ResourceStateError

class AuthorCannotBeAssigneeError(ResourceStateError):
    def __init__(self, message: str = "author cannot be assigned to their own course") -> None:
        super().__init__(message)

class ArchivedCourseError(DomainError):
    def __init__(self, message: str = "cannot modify an archived course") -> None:
        super().__init__(message)

class AlreadyArchivedError(ResourceStateError):
    def __init__(self, message: str = "already archived") -> None:
        super().__init__(message)

class NotArchivedError(ResourceStateError):
    def __init__(self, message: str = "not archived") -> None:
        super().__init__(message)

# --- DomainAuthorizationError

class NotCourseAuthorError(DomainAuthorizationError):
    def __init__(self, message: str = "only the course author can perform this action") -> None:
        super().__init__(message)

# --- EntityNotFoundError

class ChapterNotFoundError(EntityNotFoundError):
    def __init__(self, chapter_id: str) -> None:
        super().__init__(f"Chapter {chapter_id} not found in this course")
