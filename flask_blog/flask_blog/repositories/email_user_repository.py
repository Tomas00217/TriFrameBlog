from datetime import datetime, timezone
from typing import Optional
from flask_blog.accounts.models import EmailUser
from flask_blog.extensions import db
from sqlalchemy import select

class EmailUserRepository:
    def get_by_email(self, email: str):
        """
        Retrieves an EmailUser by email.

        Args:
            email (str): The email address to search for.

        Returns:
            EmailUser or None: The EmailUser object if found, or None if no match is found.
        """
        stmt = select(EmailUser).filter_by(email=email)
        result = db.session.execute(stmt).scalar_one_or_none()

        return result

    def create(self,
            email: str,
            password: str,
            username: Optional[str] = None,
            is_active: Optional[bool] = True,
            is_staff: Optional[bool] = False,
            created_at: Optional[datetime] = datetime.now(timezone.utc).replace(tzinfo=None)
        ):
        """
        Creates a new EmailUser.

        Args:
            email (str): The email of the new user.
            password (str): The password of the new user.
            username (Optional[str], optional): The username of the new user. Defaults to None.
            is_active (Optional[bool], optional): Whether the user is active. Defaults to True.
            is_staff (Optional[bool], optional): Whether the user is a staff member. Defaults to False.
            created_at (Optional[datetime], optional): The creation timestamp. Defaults to current UTC time without tzinfo.

        Returns:
            EmailUser: The newly created EmailUser object.
        """
        user = EmailUser(email=email, password=password)
        user.username = username
        user.is_active = is_active
        user.is_staff = is_staff
        user.created_at = created_at

        db.session.add(user)
        db.session.commit()

        return user

    def update(self, user: EmailUser):
        """
        Updates the EmailUser's data.

        Args:
            user (EmailUser): The EmailUser object to update.

        Returns:
            None
        """
        db.session.merge(user)
        db.session.commit()

    def get_by_id(self, user_id: int):
        """
        Retrieves an EmailUser by their ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            EmailUser or None: The EmailUser object if found, or None if no match is found.
        """
        stmt = select(EmailUser).where(EmailUser.id == user_id)
        result = db.session.execute(stmt).scalar_one_or_none()

        return result