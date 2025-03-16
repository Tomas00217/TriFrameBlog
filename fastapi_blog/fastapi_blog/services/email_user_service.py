from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends
from fastapi_blog.accounts.exceptions import EmailAlreadyExistsError
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.repositories.email_user_repository import EmailUserRepository, get_email_user_repository

class EmailUserService:
    def __init__(self, email_user_repo: EmailUserRepository):
        """
        Initializes the EmailUserService with a repository for user operations.

        Args:
            email_user_repo: An instance of the EmailUserRepository for user-related operations.
        """
        self.user_repo = email_user_repo

    async def get_user_by_email(self, email: str):
        """
        Retrieves a user by their email address.

        This method uses the provided email to query the repository and fetch 
        the corresponding user. If the user is found, the method returns the 
        user object; otherwise, it returns None.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            EmailUser or None: The user object if a user with the specified email exists, or None if no such user is found.
        """
        return await self.user_repo.get_by_email(email)
    
    async def register_user(self, email: str, password: str):
        """
        Registers a new user by hashing their password and saving their data.

        Args:
            email (str): The email address for the new user.
            password (str): The plain-text password for the new user.

        Returns:
            EmailUser: The newly created EmailUser object.

        Raises:
            EmailAlreadyExistsError: If the provided email is already in use.
        """
        user = await self.user_repo.get_by_email(email)
        if user:
            raise EmailAlreadyExistsError(email)

        return await self.user_repo.create(email=email, password=password)

    async def create_user(self,
            email: str,
            password: str,
            username: Optional[str] = None,
            is_active: bool = True,
            is_staff: bool = False,
            created_at: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
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
            is_active (bool): Flag indicating if the account is active (default is True).
            is_staff (bool): Flag indicating if the user has staff privileges (default is False).
            created_at (datetime): Timestamp of user creation (defaults to current UTC time).

        Returns:
            EmailUser: The newly created user object.

        Raises:
            EmailAlreadyExistsError: If the provided email is already in use.
        """
        user = await self.user_repo.get_by_email(email)
        if user:
            raise EmailAlreadyExistsError(email)

        new_user = await self.user_repo.create(email, password, username, is_active, is_staff, created_at)
        return new_user

    async def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        password: Optional[str] = None,
        username: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_staff: Optional[bool] = None
    ) -> EmailUser:
        """
        Updates an existing user with the provided information.
        
        Args:
            user_id (int): The ID of the user to update
            email (Optional[str]): New email address
            password (Optional[str]): New password if changing
            username (Optional[str]): New username
            is_active (Optional[bool]): User active status
            is_staff (Optional[bool]): User staff status
            
        Returns:
            EmailUser: The updated user object
            
        Raises:
            ValueError: If the user doesn't exist
            EmailAlreadyExistsError: If the email is already used
        """
        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise ValueError(f"User with ID {user_id} not found")

        if email is not None and email != user.email:
            existing_user = await self.user_repo.get_by_email(email)
            if existing_user and existing_user.id != user_id:
                raise EmailAlreadyExistsError(email)
            user.email = email

        if password is not None:
            user.set_password(password)

        if username is not None:
            user.username = username

        if is_active is not None:
            user.is_active = is_active

        if is_staff is not None:
            user.is_staff = is_staff

        updated_user = await self.user_repo.update(user)

        return updated_user

    async def update_username(self, user: EmailUser, new_username: str):
        """
        Updates the user's profile with a new username.

        Args:
            user (EmailUser): The user object to update.
            new_username (str): The new username to assign.

        Returns:
            EmailUser: The updated EmailUser object.
        """
        user.username = new_username
        return await self.user_repo.update(user)

def get_email_user_service(email_user_repo: EmailUserRepository = Depends(get_email_user_repository)):
    return EmailUserService(email_user_repo)