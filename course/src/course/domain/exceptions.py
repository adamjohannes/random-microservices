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
    Raised when a user attemps an action they don't have permission for.
    The delivery layer will map this to a 403 Forbidden.
    """

class NotCourseAuthorError(DomainAuthorizationError):
    def __init__(self, message: str = "only the course author can perform this action") -> None:
        super().__init__(message)

# --- Specific State Errors

class AlreadyArchivedError(ResourceStateError):
    def __init__(self, message: str = "already archived") -> None:
        super().__init__(message)

class NotArchivedError(ResourceStateError):
    def __init__(self, message: str = "not archived") -> None:
        super().__init__(message)
