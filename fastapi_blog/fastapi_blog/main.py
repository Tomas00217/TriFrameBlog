from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_blog.accounts.routes import accounts_router
from fastapi_blog.blogs.routes import blogs_router
from fastapi_blog.config import settings

app = FastAPI(title="TriFrameBlog")
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(blogs_router, prefix="", tags=["blogs"])