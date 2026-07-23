class AlreadyArchivedError(Exception):
    def __init__(self, message: str = "already archived") -> None:
        super().__init__(message)

class NotArchivedError(Exception):
    def __init__(self, message: str = "not archived") -> None:
        super().__init__(message)
