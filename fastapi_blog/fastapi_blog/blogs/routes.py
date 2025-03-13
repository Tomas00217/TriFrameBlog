from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
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

@blogs_router.get("/blog", response_class=HTMLResponse)
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
