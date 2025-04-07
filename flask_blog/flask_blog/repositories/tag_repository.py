from typing import List
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

    def get_by_ids(self, tag_ids: List[int]):
        """
        Retrieves multiple tags by their unique identifiers (IDs).

        Args:
            tag_ids (list): A list of tag IDs to retrieve.

        Returns:
            list: A list of Tag objects corresponding to the specified IDs.
        """
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        return db.session.execute(stmt).scalars().all()