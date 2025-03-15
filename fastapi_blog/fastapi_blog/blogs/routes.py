from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.auth import manager
from fastapi_blog.blogs.forms import BlogPostForm, DeleteBlogPostForm
from fastapi_blog.blogs.schemas import BlogQueryParams
from fastapi_blog.services.blog_post_service import BlogPostService, get_blog_post_service
from fastapi_blog.services.tag_service import TagService, get_tag_service
from fastapi_blog.templating import templates, toast
from starlette_wtf import csrf_protect
from starlette.status import HTTP_303_SEE_OTHER

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

@blogs_router.get("/blogs/create", response_class=HTMLResponse)
async def create_page(
    request: Request,
    tag_service: Annotated[BlogPostService, Depends(get_tag_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    all_tags = await tag_service.get_all()
    form = BlogPostForm(all_tags=all_tags, request=request)

    return templates.TemplateResponse(
        "create.html", {"request": request, "form": form}
    )

@blogs_router.post("/blogs/create")
@csrf_protect
async def create(
    request: Request,
    tag_service: Annotated[BlogPostService, Depends(get_tag_service)],
    blog_post_service: Annotated[BlogPostService, Depends(get_blog_post_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    all_tags = await tag_service.get_all()
    formdata = await request.form()
    form = BlogPostForm(all_tags=all_tags, request=request, formdata=formdata)

    if not await form.validate_on_submit():
        form.image.data = None
        return templates.TemplateResponse("create.html",
            {"request": request, "form": form, "errors": form.errors}
        )

    uploaded_file = formdata.get("image")
    image_bytes = await uploaded_file.read() if uploaded_file else None

    await blog_post_service.create_blog_post(
        title=form.title.data,
        content=form.content.data,
        image=image_bytes,
        author=user,
        tag_ids=form.tags.data
    )

    toast(request, "Blog created successfully!", "success")
    return RedirectResponse(url="/blogs/my", status_code=HTTP_303_SEE_OTHER)

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

@blogs_router.get("/blogs/{blog_id}/edit")
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
                "403.html", {"request": request}
            )

        all_tags = await tag_service.get_all()
        form = BlogPostForm(all_tags=all_tags, request=request, obj=blog)
        form.tags.data = [tag.id for tag in blog.tags]

        return templates.TemplateResponse(
            "edit.html", {"request": request, "form": form, "blog": blog}
        )
    except ValueError:
        return templates.TemplateResponse(
            "404.html", {"request": request}
        )

@blogs_router.post("/blogs/{blog_id}/edit")
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
                "403.html", {"request": request}
            )

        all_tags = await tag_service.get_all()
        formdata = await request.form()
        form = BlogPostForm(all_tags=all_tags, request=request, formdata=formdata)

        if not await form.validate_on_submit():
            form.image.data = blog.image
            return templates.TemplateResponse("edit.html",
                {"request": request, "form": form, "errors": form.errors, "blog": blog}
        )

        uploaded_file = formdata.get("image")
        image_bytes = await uploaded_file.read() if uploaded_file else None

        await blog_post_service.update_blog_post(
            blog_id=blog.id,
            title=form.title.data,
            content=form.content.data,
            image=image_bytes,
            tag_ids=form.tags.data
        )

        toast(request, "Blog updated successfully!", "success")
        return RedirectResponse(url="/blogs/my", status_code=HTTP_303_SEE_OTHER)
    except ValueError:
        return templates.TemplateResponse(
            "404.html", {"request": request}
        )

@blogs_router.get("/blogs/{blog_id}/delete")
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
                "403.html", {"request": request}
            )

        return templates.TemplateResponse(
            "delete.html", {"request": request, "blog": blog, "form": form}
        )
    except ValueError:
        return templates.TemplateResponse(
            "404.html", {"request": request}
        )
    
@blogs_router.post("/blogs/{blog_id}/delete")
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
                "403.html", {"request": request}
            )
        
        if await form.validate_on_submit():
            await blog_post_service.delete_blog_post(blog_id)

        toast(request, "Blog deleted successfully!", "success")
        return RedirectResponse(url="/blogs/my", status_code=HTTP_303_SEE_OTHER)
    except ValueError:
        return templates.TemplateResponse(
            "404.html", {"request": request}
        )