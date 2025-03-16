from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.database import get_session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

class EmailUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: int):
        """
        Retrieves an EmailUser by id.

        Args:
            id (int): The id to search for.

        Returns:
            EmailUser or None: The EmailUser object if found, or None if no match is found.
        """
        stmt = select(EmailUser).filter_by(id=id)
        result = await self.db.exec(stmt)

        return result.one_or_none()

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
    
    async def create(
            self,
            email: str,
            password: str,
            username: Optional[str] = None,
            is_active: bool = True,
            is_staff: bool = False,
            created_at: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
            ):
        """
        Creates a new EmailUser.

        Args:
            email (str): The email of the new user.
            password (str): The password of the new user.

        Returns:
            EmailUser: The newly created EmailUser object.
        """
        user = EmailUser(email=email, username=username, is_active=is_active, is_staff=is_staff, created_at=created_at)
        user.set_password(password)

        self.db.add(user)
        await self.db.commit()

        return user

    async def update(self, user: EmailUser):
        """
        Updated the EmailUser.

        Args:
            user (EmailUser): The user to update.

        Returns:
            EmailUser: The updated EmailUser object.
        """
        await self.db.merge(user)
        await self.db.commit()

        return user

def get_email_user_repository(db: AsyncSession = Depends(get_session)):
    return EmailUserRepository(db)