from typing import List, Optional
from fastapi import Depends
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.blogs.models import BlogPost
from fastapi_blog.repositories.blog_post_repository import BlogPostRepository, get_blog_post_repository


class BlogPostService:
    def __init__(self, blog_repo: BlogPostRepository):
        """
        Initializes the BlogPostService with repositories for blog posts and tags.

        Args:
            blog_repo: An instance of the BlogPostRepository for blog operations.
            tag_repo: An instance of the TagRepository for tag-related operations.
        """
        self.blog_repo = blog_repo

    async def get_recent_blogs(self, limit: int = 3):
        """
        Retrieves the most recent blog posts.

        Args:
            limit (int, optional): The maximum number of recent blog posts to retrieve. Defaults to 3.

        Returns:
            list: A list of BlogPost objects representing the most recent blogs.
        """
        return await self.blog_repo.get_recent(limit)
    
    async def get_paginated_blogs(self, tag_slugs: List[str], search: Optional[str], page: int, per_page: int):
        """
        Retrieves paginated blog posts, optionally filtered by tags or search term.

        Args:
            tag_slugs (list, optional): A list of tag slugs to filter blogs by tags.
            search (str, optional): A search term to filter blogs by title. 
            page (int, optional): The page number for pagination.
            per_page (int, optional): The number of blogs per page.

        Returns:
            PaginatedResult: A paginated result set containing BlogPost objects.
        """
        stmt = self.blog_repo.get_all_query(tag_slugs, search)
        return await self.blog_repo.get_paginated(stmt, page, per_page)
    
    async def get_blog_by_id(self, blog_id: int):
        """
        Retrieves a single blog post by its unique identifier (ID).

        Args:
            blog_id (int): The ID of the blog post to retrieve.

        Raises:
            ValueError: If no blog post is found with the given ID.

        Returns:
            BlogPost: The BlogPost object corresponding to the provided ID.
        """
        blog = await self.blog_repo.get_by_id(blog_id)
        if not blog:
            raise ValueError("Blog post not found")

        return blog

    async def get_related_blogs(self, blog: BlogPost, limit: int = 3):
        """
        Retrieves related blog posts based on shared tags, excluding the current blog.

        Args:
            blog (BlogPost): The current blog post used to find related blogs.
            limit (int, optional): The maximum number of related blog posts to return. Defaults to 3.

        Returns:
            list: A list of related BlogPost objects.
        """
        return await self.blog_repo.get_related(blog, limit=limit)

    async def get_paginated_user_blogs(self, user: EmailUser, page: int = 1, per_page: int = 6):
        """
        Retrieves paginated blog posts authored by a specific user.

        Args:
            user (EmailUser): The user whose paginated blog posts are to be retrieved.
            page (int, optional): The page number for pagination. Defaults to 1.
            per_page (int, optional): The number of blog posts per page. Defaults to 6.

        Returns:
            Pagination: A paginated result set containing BlogPost objects authored by the specified user.
        """
        stmt = self.blog_repo.get_by_author_query(user)
        return await self.blog_repo.get_paginated(stmt, page, per_page)

def get_blog_post_service(blog_post_repo: BlogPostRepository = Depends(get_blog_post_repository)):
    return BlogPostService(blog_post_repo)