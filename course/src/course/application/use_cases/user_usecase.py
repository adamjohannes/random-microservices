from uuid import UUID

from src.course.domain.user import User
from src.course.domain.user_email import UserEmail
from src.course.domain.user_name import UserName
from src.course.application.ports.user_repository import UserRepository


class UserUseCase:
    """
    Orchestrates the user-related business transactions.
    """

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def sync_user(self, account_id: UUID, name: str, email: str) -> User:
        """
        Creates or updates a user mirrored from the Account service.
        On update, calls the database only if something changed.

        Args:
            account_id: The user ID mirroring the Account service account_id.
            name: The name for the new user.
            email: The email for the new user.

        Returns:
            The newly created or updated user.

        Raises:
            InvalidNameLenghtError: If name_str is not 2-50 characters.
            InvalidNameCharacterError: If name_str contains non-alphabetical characters.
            EmptyEmailError: If email_str is empty.
            InvalidEmailFormatError: If email_str is not a valid email.
        """
        changed = False
        user = await self._user_repo.get_by_id(account_id)

        if user is None:
            # Create a new user
            user = User.create(account_id=account_id, name_str=name, email_str=email)
            changed = True
        else:
            # Update user if something changed
            if str(user.name) != name:
                user.update_name(UserName(name))
                changed = True
            if str(user.email) != email:
                user.update_email(UserEmail(email))
                changed = True

        if changed:
            await self._user_repo.save(user)

        return user
