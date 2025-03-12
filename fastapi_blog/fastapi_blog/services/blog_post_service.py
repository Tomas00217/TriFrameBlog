from typing import List, Optional
from fastapi import Depends
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

def get_blog_post_service(blog_post_repo: BlogPostRepository = Depends(get_blog_post_repository)):
    return BlogPostService(blog_post_repo)