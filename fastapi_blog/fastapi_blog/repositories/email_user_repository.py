from fastapi import Depends
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.database import get_session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

class EmailUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str):
        """
        Retrieves an EmailUser by email.

        Args:
            email (str): The email address to search for.

        Returns:
            EmailUser or None: The EmailUser object if found, or None if no match is found.
        """
        stmt = select(EmailUser).filter_by(email=email)
        result = await self.db.exec(stmt)

        return result.one_or_none()
    
    async def create(self, email: str, password: str):
        """
        Creates a new EmailUser.

        Args:
            email (str): The email of the new user.
            password (str): The password of the new user.

        Returns:
            EmailUser: The newly created EmailUser object.
        """
        user = EmailUser(email=email, password=password)
        self.db.add(user)
        await self.db.commit()

        return user

    async def update(self, user: EmailUser):
        await self.db.merge(user)
        await self.db.commit()

        return user

def get_email_user_repository(db: AsyncSession = Depends(get_session)):
    return EmailUserRepository(db)