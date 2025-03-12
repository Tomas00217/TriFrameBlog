from typing import List, Optional
from fastapi import Depends
from fastapi_blog.blogs.models import BlogPost, Tag
from fastapi_blog.blogs.schemas import PaginatedResponse
from fastapi_blog.database import get_session
from sqlmodel import func, select
from sqlalchemy.orm import joinedload
from sqlmodel.ext.asyncio.session import AsyncSession

class BlogPostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_recent(self, limit: int = 3):
        """
        Retrieves the most recent blog posts, ordered by creation date.

        Args:
            limit (int, optional): The maximum number of recent blog posts to return. Defaults to 3.

        Returns:
            list: A list of the most recent BlogPost objects.
        """
        stmt = select(BlogPost).options(joinedload(BlogPost.tags)).order_by(BlogPost.created_at.desc()).limit(limit)
        result = await self.db.exec(stmt)

        return result.unique().all()

    def get_all_query(self, tag_slugs: List[str], search: Optional[str] = None):
        """
        Constructs a query to retrieve blog posts, optionally filtered by tags or search terms.

        Args:
            tag_slugs (list, optional): A list of tag slugs to filter the blogs by tags. Defaults to None.
            search (str, optional): A search string to filter blogs by title. Defaults to None.

        Returns:
           The select statement to retrieve filtered blogs.
        """
        stmt = select(BlogPost).options(joinedload(BlogPost.tags)).order_by(BlogPost.created_at.desc())

        if tag_slugs:
            for tag_slug in tag_slugs:
                stmt = stmt.filter(BlogPost.tags.any(Tag.slug == tag_slug))

        if search:
            stmt = stmt.filter(BlogPost.title.ilike(f"%{search}%"))

        stmt = stmt.order_by(BlogPost.created_at.desc()).distinct()
        return stmt

    async def get_all(self, tag_slugs: List[str], search: Optional[str] = None):
        """
        Executes the constructed query to retrieve all blog posts, optionally filtered by tags or search terms.

        Args:
            tag_slugs (list, optional): A list of tag slugs to filter the blogs by tags. Defaults to None.
            search (str, optional): A search string to filter blogs by title. Defaults to None.

        Returns:
            list: A list of BlogPost objects matching the query criteria.
        """
        stmt = self.get_all_query(tag_slugs, search)
        result = await self.db.exec(stmt)
        
        return result.unique().all()

    async def get_paginated(self, stmt, page: int = 1, per_page: int = 6):
        """
        Paginates a given query statement.

        Args:
            stmt: The SQLAlchemy select statement to paginate.
            page (int): The page number for pagination.
            per_page (int): The number of items per page.

        Returns:
            PaginatedResponse: A paginated result with blog posts.
        """
        count_stmt = select(func.count()).select_from(stmt)
        total_count = (await self.db.exec(count_stmt)).one()

        paginated_stmt = stmt.offset((page - 1) * per_page).limit(per_page)
        results = await self.db.exec(paginated_stmt)
        data = results.unique().all()

        total_pages = (total_count + per_page - 1) // per_page
        next_page = page + 1 if page * per_page < total_count else None
        prev_page = page - 1 if page > 1 else None

        return PaginatedResponse[BlogPost](
            data=data,
            total=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            next_page=next_page,
            prev_page=prev_page,
        )

def get_blog_post_repository(db: AsyncSession = Depends(get_session)):
    return BlogPostRepository(db)
