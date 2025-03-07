from flask_blog.blogs.models import Tag
from flask_blog.extensions import db
from sqlalchemy import select

class TagRepository:
    def get_all(self):
        """
        Retrieves all tag records from the database.

        Returns:
            list: A list of all Tag objects in the database.
        """
        stmt = select(Tag)
        return db.session.execute(stmt).scalars().all()

    def get_by_id(self, tag_id):
        """
        Retrieves a tag by its unique identifier (ID).

        Args:
            tag_id (int): The ID of the tag to retrieve.

        Returns:
            Tag or None: The Tag object if found, or None if no tag with the specified ID exists.
        """
        stmt = select(Tag).where(Tag.id == tag_id)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_by_ids(self, tag_ids):
        """
        Retrieves multiple tags by their unique identifiers (IDs).

        Args:
            tag_ids (list): A list of tag IDs to retrieve.

        Returns:
            list: A list of Tag objects corresponding to the specified IDs.
        """
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        return db.session.execute(stmt).scalars().all()