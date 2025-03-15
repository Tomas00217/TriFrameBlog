from typing import Annotated, List, Optional
import bleach
import cloudinary.uploader
from fastapi import Depends
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.blogs.models import BlogPost
from fastapi_blog.repositories.blog_post_repository import BlogPostRepository, get_blog_post_repository
from fastapi_blog.repositories.tag_repository import TagRepository, get_tag_repository


class BlogPostService:
    def __init__(self, blog_repo: BlogPostRepository, tag_repo: TagRepository):
        """
        Initializes the BlogPostService with repositories for blog posts and tags.

        Args:
            blog_repo: An instance of the BlogPostRepository for blog operations.
            tag_repo: An instance of the TagRepository for tag-related operations.
        """
        self.blog_repo = blog_repo
        self.tag_repo = tag_repo

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

    async def create_blog_post(self, title: str, content: str, image: str, author: EmailUser, tag_ids: List[int]):
        """
        Creates a new blog post with the provided details.

        Args:
            title (str): The title of the new blog post.
            content (str): The content or body of the new blog post.
            image (str): The image associated with the new blog post.
            author (User): The author of the new blog post.
            tag_ids (list): A list of tag IDs to associate with the new blog post.

        Returns:
            BlogPost: The newly created BlogPost object.
        """
        content = self.clean_content(content)
        image_url = self.upload_image(image)
        tags = await self.tag_repo.get_by_ids(tag_ids)

        return await self.blog_repo.create(title, content, image_url, author, tags)

    async def update_blog_post(self, blog_id: int, title: str, content: str, image: str, tag_ids: List[int]):
        """
        Updates an existing blog post with new data.

        Args:
            blog_id (int): The ID of the blog post to update.
            title (str): The new title for the blog post.
            content (str): The new content for the blog post.
            image (str): The new image for the blog post (if provided).
            tag_ids (list): A list of tag IDs to associate with the updated blog post.

        Raises:
            abort(404): If the blog post with the provided ID does not exist.

        Returns:
            BlogPost: The updated BlogPost object.
        """
        blog = await self.blog_repo.get_by_id(blog_id)
        if not blog:
            raise ValueError("Blog post not found")

        tags = await self.tag_repo.get_by_ids(tag_ids)
        content = self.clean_content(content)
        image_url = self.upload_image(image) if image else blog.image

        return await self.blog_repo.update(blog, title, content, image_url, tags)

    async def delete_blog_post(self, blog_id: int):
        """
        Deletes a blog post by its ID.

        Args:
            blog_id (int): The ID of the blog post to delete.

        Raises:
            abort(404): If no blog post is found with the provided ID.

        Returns:
            None
        """
        blog = await self.blog_repo.get_by_id(blog_id)
        if not blog:
            raise ValueError("Blog post not found")

        return await self.blog_repo.delete(blog)

    def clean_content(self, content):
        """
        Cleans the provided content by removing any disallowed HTML tags and attributes.

        Args:
            content (str): The content (HTML) to clean.

        Returns:
            str: The cleaned content, safe for rendering in the application.
        """
        allowed_tags = ["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"]
        allowed_attrs = {"a": ["href", "target"], "span": ["class", "contenteditable"]}

        return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)

    def upload_image(self, image_file):
        """
        Uploads an image file to Cloudinary and returns the secure URL of the uploaded image.

        Args:
            image_file (file): The image file to upload.

        Returns:
            str or None: The secure URL of the uploaded image, or None if no image is provided.
        """
        if not image_file:
            return None

        upload_result = cloudinary.uploader.upload(image_file)

        return upload_result["secure_url"]

def get_blog_post_service(blog_post_repo: Annotated[BlogPostRepository, Depends(get_blog_post_repository)], tag_repo: Annotated[TagRepository, Depends(get_tag_repository)]):
    return BlogPostService(blog_post_repo, tag_repo)