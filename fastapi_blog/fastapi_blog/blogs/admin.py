from typing import Any, Dict
from fastapi import Request
from fastapi_blog.admin import AdminView
from fastapi_blog.database import async_engine
from fastapi_blog.blogs.models import BlogPost
from fastapi_blog.repositories.blog_post_repository import get_blog_post_repository
from fastapi_blog.repositories.email_user_repository import get_email_user_repository
from fastapi_blog.repositories.tag_repository import get_tag_repository
from fastapi_blog.services.blog_post_service import BlogPostService, get_blog_post_service
from starlette_admin import FileField
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

class BlogPostView(AdminView):
    model = BlogPost
    identity = "blog-post"
    name = "BlogPost"
    label = "BlogPosts"
    icon = "blogposts"

    fields = ["id", "title", "content", "image", FileField("upload_image", label="Upload New Image"), "created_at", "author", "tags"]

    exclude_fields_from_list = ["content", "image", "upload_image"]
    exclude_fields_from_create = ["image", "created_at"]
    exclude_fields_from_detail = ["upload_image"]

    async def get_blog_service(self) -> BlogPostService:
        Session = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with Session() as session:
            tag_repo = get_tag_repository(session)
            blog_repo = get_blog_post_repository(session)
            user_repo = get_email_user_repository(session)
            blog_service = get_blog_post_service(blog_repo, tag_repo, user_repo)
            return blog_service

    async def create(self, request: Request, data: Dict) -> BlogPost:
        try:
            blog_service = await self.get_blog_service()

            uploaded_file = data.pop("upload_image", None)

            title = data.get("title")
            content = data.get("content")
            image = await uploaded_file[0].read() if uploaded_file[0] else None 
            author_id = int(data.get("author"))
            tags = data.get("tags")
            tag_ids = [int(tag) for tag in tags]

            blog = await blog_service.create_blog_post(
                title=title,
                content=content,
                image=image,
                author_id=author_id,
                tag_ids=tag_ids
            )

            return blog
        except Exception as e:
            raise e

    async def edit(self, request: Request, pk: Any, data: Dict) -> BlogPost:
        try:
            blog_service = await self.get_blog_service()

            uploaded_file = data.pop("upload_image", None)

            title = data.get("title")
            content = data.get("content")
            image = await uploaded_file[0].read() if uploaded_file[0] else None 
            author_id = int(data.get("author"))
            tags = data.get("tags")
            tag_ids = [int(tag) for tag in tags]
            created_at = data.get("created_at")

            blog = await blog_service.update_blog_post(
                blog_id=int(pk),
                title=title,
                content=content,
                image=image,
                author_id=author_id,
                tag_ids=tag_ids,
                created_at=created_at
            )

            return blog
        except Exception as e:
            raise e