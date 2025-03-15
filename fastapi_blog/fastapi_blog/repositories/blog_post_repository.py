from typing import List, Optional
from fastapi import Depends
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.blogs.models import BlogPost, Tag
from fastapi_blog.blogs.schemas import PaginatedResponse
from fastapi_blog.database import get_session
from sqlmodel import func, select, update
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
    
    async def get_by_id(self, blog_id: int):
        """
        Retrieves a blog post by its unique identifier (ID).

        Args:
            blog_id (int): The ID of the blog post.

        Returns:
            BlogPost or None: The BlogPost object if found, or None if no blog with the specified ID exists.
        """
        stmt = (
            select(BlogPost)
            .options(joinedload(BlogPost.tags))
            .options(joinedload(BlogPost.author))
            .filter(BlogPost.id == blog_id)
        )
        result = await self.db.exec(stmt)

        return result.unique().one_or_none()

    async def get_related(self, blog: BlogPost, limit: int = 3):
        """
        Retrieves related blog posts based on shared tags, excluding the current blog post.

        Args:
            blog (BlogPost): The blog post to find related posts for.
            limit (int, optional): The maximum number of related blog posts to return. Defaults to 3.

        Returns:
            list: A list of BlogPost objects related to the specified blog post.
        """
        stmt = (
            select(BlogPost)
            .options(joinedload(BlogPost.tags))
            .filter(Tag.id.in_([tag.id for tag in blog.tags]))
            .filter(BlogPost.id != blog.id)
            .group_by(BlogPost.id)
            .order_by(BlogPost.id, func.random())
            .limit(limit)
        )
        result = await self.db.exec(stmt)

        return result.unique().all()
    
    def get_by_author_query(self, user: EmailUser):
        """
        Constructs a query to retrieve all blog posts authored by a specific user.

        Args:
            user (User): The user whose blogs are to be retrieved.

        Returns:
            The select statement to retrieve blogs by the specified author.
        """
        return (
            select(BlogPost)
            .options(joinedload(BlogPost.tags))
            .filter(BlogPost.author_id == user.id)
            .order_by(BlogPost.created_at.desc())
        )

    async def create(self, title: str, content: str, image: str, author: EmailUser, tags: List[Tag]):
        """
        Creates and persists a new blog post in the database.

        Args:
            title (str): The title of the new blog post.
            content (str): The content/body of the new blog post.
            image (str): The URL or file path to the image associated with the new blog post.
            author (EmailUser): The author of the new blog post.
            tags (list): A list of Tag objects to associate with the new blog post.

        Returns:
            BlogPost: The created BlogPost object.
        """
        blog_post = BlogPost(title=title, content=content, image=image, author=author)
        if tags:
            blog_post.tags = tags
        
        self.db.add(blog_post)
        await self.db.commit()

        return blog_post

    async def update(self, blog: BlogPost, title: str, content: str, image: str, tags: List[Tag]):
        """
        Updates an existing blog post with new data.

        Args:
            blog (BlogPost): The blog post to update.
            title (str): The new title for the blog post.
            content (str): The new content for the blog post.
            image (str): The new image URL or file path for the blog post.
            tags (list): A list of new Tag objects to associate with the blog post.

        Returns:
            BlogPost: The updated BlogPost object.
        """
        stmt = (
            update(BlogPost)
            .where(BlogPost.id == blog.id)
            .values(title=title, content=content, image=image)
        )
        await self.db.exec(stmt)
        blog.tags = tags
        await self.db.commit()

        return blog

    async def delete(self, blog: BlogPost):
        """
        Deletes a blog post from the database.

        Args:
            blog (BlogPost): The blog post to delete.

        Returns:
            None
        """
        await self.db.delete(blog)
        await self.db.commit()

def get_blog_post_repository(db: AsyncSession = Depends(get_session)):
    return BlogPostRepository(db)
