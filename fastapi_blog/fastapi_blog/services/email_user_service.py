from fastapi import Depends
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
            EmailUser or None: The user object if a user with the specified email exists, 
                            or None if no such user is found.
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
        """
        return await self.user_repo.create(email=email, password=password)
    
    async def update_user(self, user: EmailUser, new_username: str):
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