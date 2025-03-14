from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.auth import manager
from fastapi_blog.blogs.schemas import BlogQueryParams
from fastapi_blog.services.blog_post_service import BlogPostService, get_blog_post_service
from fastapi_blog.services.tag_service import TagService, get_tag_service
from fastapi_blog.templating import templates

blogs_router = APIRouter()

@blogs_router.get("/", response_class=HTMLResponse)
async def index(
    request: Request,
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    tag_service: Annotated[TagService, Depends(get_tag_service)],
):
    blogs = await blog_post_service.get_recent_blogs()
    tags = await tag_service.get_all()

    return templates.TemplateResponse(
        "index.html", {"request": request, "blogs": blogs, "tags": tags}
    )

@blogs_router.get("/blogs", response_class=HTMLResponse)
async def blogs(
    request: Request,
    query_params: Annotated[BlogQueryParams, Depends()],
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    tag_service: Annotated[TagService, Depends(get_tag_service)],
):
    tag_slugs_list = query_params.tag.split(",") if query_params.tag else []

    result = await blog_post_service.get_paginated_blogs(tag_slugs_list, query_params.search, query_params.page, query_params.per_page)
    tags = await tag_service.get_all()

    return templates.TemplateResponse(
        "blogs.html", {"request": request, "result": result, "tags": tags, "selected_tags": tag_slugs_list}
    )

@blogs_router.get("/blogs/my", response_class=HTMLResponse)
async def my_blogs(
    request: Request, 
    query_params: Annotated[BlogQueryParams, Depends()],
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    result = await blog_post_service.get_paginated_user_blogs(user, query_params.page, query_params.per_page)

    return templates.TemplateResponse(
        "my_blogs.html", {"request": request, "result": result}
    )

@blogs_router.get("/blogs/{blog_id}", response_class=HTMLResponse)
async def detail(
    request: Request, 
    blog_id: int,
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)]
):
    try:
        blog = await blog_post_service.get_blog_by_id(blog_id)
        related_blogs = await blog_post_service.get_related_blogs(blog)

        return templates.TemplateResponse(
            "detail.html", {"request": request, "blog": blog, "related_blogs": related_blogs}
        )
    except ValueError:
        return templates.TemplateResponse(
            "404.html", {"request": request}
        )