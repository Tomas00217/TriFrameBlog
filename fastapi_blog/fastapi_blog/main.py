from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_blog.accounts.routes import accounts_router
from fastapi_blog.blogs.routes import blogs_router
from fastapi_blog.config import settings
from fastapi_blog.exceptions import NotAuthenticatedException
from fastapi_blog.auth import manager

app = FastAPI(title="TriFrameBlog")

manager.attach_middleware(app)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(blogs_router, prefix="", tags=["blogs"])

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    return RedirectResponse(url="/accounts/login")

