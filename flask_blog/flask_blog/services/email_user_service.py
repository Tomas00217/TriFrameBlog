from datetime import datetime, timezone
from typing import Optional
from flask_blog.accounts.exceptions import EmailAlreadyExistsError
from flask_blog.accounts.models import EmailUser
from flask_blog.repositories.email_user_repository import EmailUserRepository

class EmailUserService:
    def __init__(self, user_repo: EmailUserRepository):
        """
        Initializes the EmailUserService with a repository for user-related operations.

        Args:
            user_repo: An instance of the EmailUserRepository for user data access.
        """
        self.user_repo = user_repo

    def register_user(self, email: str, password: str):
        """
        Registers a new user by hashing their password and saving their data.

        Args:
            email (str): The email address for the new user.
            password (str): The plain-text password for the new user.

        Returns:
            EmailUser: The newly created EmailUser object.
        """
        user = self.user_repo.get_by_email(email)
        if user:
            raise EmailAlreadyExistsError(email)

        return self.user_repo.create(email=email, password=password)

    def get_user_by_email(self, email: str):
        """
        Retrieves a user by their email address.

        This method uses the provided email to query the repository and fetch 
        the corresponding user. If the user is found, the method returns the 
        user object; otherwise, it returns None.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            EmailUser or None: The user object if a user with the specified email exists, 
                            or None if no such user is found.
        """
        return self.user_repo.get_by_email(email)

    def update_user(self, user: EmailUser, new_username: str):
        """
        Updates the user's profile with a new username.

        Args:
            user (EmailUser): The user object to update.
            new_username (str): The new username to assign.

        Returns:
            None
        """
        user.username = new_username
        self.user_repo.update(user)

    def create_user(self, 
            email: str, 
            password: str, 
            username: Optional[str] = None, 
            is_active: Optional[bool] = True, 
            is_staff: Optional[bool] = False, 
            created_at: Optional[datetime] = datetime.now(timezone.utc).replace(tzinfo=None)
        ):
        """
        Creates a new user in the system.

        Checks if the provided email is already in use. If the email exists, raises 
        `EmailAlreadyExistsError`. Otherwise, creates a new user with the provided 
        details and returns the user object.

        Parameters:
            email (str): The email address of the user. Must be unique.
            password (str): The password for the user (will be hashed).
            username (Optional[str]): The username of the user (default is None).
            is_active (Optional[bool]): Flag indicating if the account is active (default is True).
            is_staff (Optional[bool]): Flag indicating if the user has staff privileges (default is False).
            created_at (Optional[datetime]): Timestamp of user creation (defaults to current UTC time).

        Returns:
            EmailUser: The newly created user object.

        Raises:
            EmailAlreadyExistsError: If the provided email is already in use.
        """
        user = self.user_repo.get_by_email(email)
        if user:
            raise EmailAlreadyExistsError(email)

        new_user = self.user_repo.create(email, password, username, is_active, is_staff, created_at)
        return new_user