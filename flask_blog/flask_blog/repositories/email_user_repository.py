from flask_blog.accounts.models import EmailUser
from flask_blog.extensions import db
from sqlalchemy import select


class EmailUserRepository:
    def get_by_email(self, email):
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

    def create(self, email, password):
        """
        Creates a new EmailUser.

        Args:
            email (str): The email of the new user.
            password (str): The password of the new user.

        Returns:
            EmailUser: The newly created EmailUser object.
        """
        user = EmailUser(email=email, password=password)
        db.session.add(user)
        db.session.commit()

        return user

    def update(self, user):
        """
        Updates the EmailUser's data.

        Args:
            user (EmailUser): The EmailUser object to update.

        Returns:
            None
        """
        db.session.merge(user)
        db.session.commit()

    def get_by_id(self, user_id):
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