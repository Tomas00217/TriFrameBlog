from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi_blog.templating import templates

blogs_router = APIRouter()

@blogs_router.get("/", response_class=HTMLResponse, name="index")
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )