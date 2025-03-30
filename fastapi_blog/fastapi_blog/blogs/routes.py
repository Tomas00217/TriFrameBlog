from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.auth import manager
from fastapi_blog.blogs.exceptions import BlogPostNotFoundError
from fastapi_blog.blogs.forms import BlogPostForm, DeleteBlogPostForm
from fastapi_blog.blogs.schemas import BlogQueryParams
from fastapi_blog.services.blog_post_service import BlogPostService, get_blog_post_service
from fastapi_blog.services.tag_service import TagService, get_tag_service
from fastapi_blog.templating import templates, toast
from starlette_wtf import csrf_protect
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from fastapi_blog.config import settings
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
        request, "index.html", {"blogs": blogs, "tags": tags}
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
        request, "blogs.html", {"result": result, "tags": tags, "selected_tags": tag_slugs_list}
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
        request, "my_blogs.html", {"result": result}
    )

@blogs_router.get("/blogs/create", response_class=HTMLResponse)
async def create_page(
    request: Request,
    tag_service: Annotated[BlogPostService, Depends(get_tag_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    all_tags = await tag_service.get_all()
    form = BlogPostForm(all_tags=all_tags, request=request)

    return templates.TemplateResponse(
        request, "create.html", {"form": form}
    )

@blogs_router.post("/blogs/create", response_class=HTMLResponse)
@csrf_protect
async def create(
    request: Request,
    tag_service: Annotated[BlogPostService, Depends(get_tag_service)],
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    try:
        all_tags = await tag_service.get_all()
        formdata = await request.form()
        form = BlogPostForm(all_tags=all_tags, request=request, formdata=formdata)

        if not await form.validate_on_submit():
            form.image.data = None
            return templates.TemplateResponse(request,
                "create.html",
                {"form": form, "errors": form.errors},
                status_code=HTTP_400_BAD_REQUEST
            )

        uploaded_file = formdata.get("image")

        blog = await blog_post_service.create_blog_post(
            title=form.title.data,
            content=form.content.data,
            image=uploaded_file,
            author_id=user.id,
            tag_ids=form.tags.data
        )

        toast(request, "Blog created successfully!", "success")
        return RedirectResponse(url=f"/blogs/{blog.id}", status_code=HTTP_303_SEE_OTHER)
    except Exception as e:
        form.image.data = None
        toast(request, "Error occured, please try again later.", "error")
        return templates.TemplateResponse(request,
            "create.html",
            {"form": form, "errors": form.errors},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
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
            request, "detail.html", {"blog": blog, "related_blogs": related_blogs}
        )
    except BlogPostNotFoundError:
        return templates.TemplateResponse(
            request, "404.html", status_code=HTTP_404_NOT_FOUND
        )

@blogs_router.get("/blogs/{blog_id}/edit", response_class=HTMLResponse)
@csrf_protect
async def edit_page(
    request: Request,
    blog_id: int,
    tag_service: Annotated[BlogPostService, Depends(get_tag_service)],
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    try:
        blog = await blog_post_service.get_blog_by_id(blog_id)

        if user != blog.author and not user.is_staff:
            return templates.TemplateResponse(
                request, "403.html", status_code=HTTP_403_FORBIDDEN
            )

        all_tags = await tag_service.get_all()
        form = BlogPostForm(all_tags=all_tags, request=request, obj=blog)
        form.tags.data = [tag.id for tag in blog.tags]

        return templates.TemplateResponse(
            request, "edit.html", {"form": form, "blog": blog}
        )
    except BlogPostNotFoundError:
        return templates.TemplateResponse(
            request, "404.html", status_code=HTTP_404_NOT_FOUND
        )

@blogs_router.post("/blogs/{blog_id}/edit", response_class=HTMLResponse)
@csrf_protect
async def edit(
    request: Request,
    blog_id: int,
    tag_service: Annotated[BlogPostService, Depends(get_tag_service)],
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    try:
        blog = await blog_post_service.get_blog_by_id(blog_id)

        if user != blog.author and not user.is_staff:
            return templates.TemplateResponse(
                request, "403.html",
            )

        all_tags = await tag_service.get_all()
        formdata = await request.form()
        form = BlogPostForm(all_tags=all_tags, request=request, formdata=formdata)

        if not await form.validate_on_submit():
            form.image.data = blog.image
            return templates.TemplateResponse(request,
                "edit.html",
                {"form": form, "errors": form.errors, "blog": blog},
                status_code=HTTP_400_BAD_REQUEST
        )

        uploaded_file = formdata.get("image")

        await blog_post_service.update_blog_post(
            blog_id=blog.id,
            title=form.title.data,
            content=form.content.data,
            image=uploaded_file,
            tag_ids=form.tags.data
        )

        toast(request, "Blog updated successfully!", "success")
        return RedirectResponse(url=f"/blogs/{blog_id}", status_code=HTTP_303_SEE_OTHER)
    except BlogPostNotFoundError:
        return templates.TemplateResponse(
            request, "404.html", status_code=HTTP_404_NOT_FOUND
        )
    except Exception:
        form.image.data = None
        toast(request, "Error occured, please try again later.", "error")
        return templates.TemplateResponse(request,
            "edit.html",
            {"form": form, "errors": form.errors, "blog": blog},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )

@blogs_router.get("/blogs/{blog_id}/delete", response_class=HTMLResponse)
async def delete_page(
    request: Request,
    blog_id: int,
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    try:
        form = await DeleteBlogPostForm.from_formdata(request)
        blog = await blog_post_service.get_blog_by_id(blog_id)

        if user != blog.author and not user.is_staff:
            return templates.TemplateResponse(
                request, "403.html", status_code=HTTP_403_FORBIDDEN
            )

        return templates.TemplateResponse(
            request, "delete.html", {"blog": blog, "form": form}
        )
    except BlogPostNotFoundError:
        return templates.TemplateResponse(
            request, "404.html", status_code=HTTP_404_NOT_FOUND
        )

@blogs_router.post("/blogs/{blog_id}/delete", response_class=HTMLResponse)
async def delete(
    request: Request,
    blog_id: int,
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    try:
        form = await DeleteBlogPostForm.from_formdata(request)
        blog = await blog_post_service.get_blog_by_id(blog_id)

        if user != blog.author and not user.is_staff:
            return templates.TemplateResponse(
                request, "403.html", status_code=HTTP_403_FORBIDDEN
            )
        
        if await form.validate_on_submit():
            await blog_post_service.delete_blog_post(blog_id)

        toast(request, "Blog deleted successfully!", "success")
        return RedirectResponse(url="/blogs/my", status_code=HTTP_303_SEE_OTHER)
    except BlogPostNotFoundError:
        return templates.TemplateResponse(
            request, "404.html", status_code=HTTP_404_NOT_FOUND
        )
    except Exception:
        toast(request, "Error occured, please try again later.", "error")
        return templates.TemplateResponse(request,
            "delete.html",
            {"form": form, "errors": form.errors, "blog": blog},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )