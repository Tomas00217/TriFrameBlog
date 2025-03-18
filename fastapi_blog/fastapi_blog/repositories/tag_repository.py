from typing import List
from fastapi import Depends
from fastapi_blog.blogs.models import Tag
from fastapi_blog.database import get_session
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        """
        Retrieves all tag records from the database.

        Returns:
            list: A list of all Tag objects in the database.
        """
        stmt = select(Tag)
        result = await self.db.exec(stmt)

        return result.all()

    async def get_by_ids(self, tag_ids: List[int]):
        """
        Retrieves multiple tags by their unique identifiers (IDs).

        Args:
            tag_ids (list): A list of tag IDs to retrieve.

        Returns:
            list: A list of Tag objects corresponding to the specified IDs.
        """
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        result = await self.db.exec(stmt)

        return result.all()
    
def get_tag_repository(db: AsyncSession = Depends(get_session)):
    return TagRepository(db)