from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_blog.accounts.admin import EmailUserView
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.accounts.routes import accounts_router
from fastapi_blog.admin import AdminIndexView, AdminView
from fastapi_blog.blogs.admin import BlogPostView
from fastapi_blog.blogs.models import BlogPost, Tag
from fastapi_blog.blogs.routes import blogs_router
from fastapi_blog.config import settings
from fastapi_blog.database import async_engine
from fastapi_blog.exceptions import NotAuthenticatedException
from fastapi_blog.auth import manager
from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import CSRFProtectMiddleware
from starlette_admin.contrib.sqlmodel import Admin

app = FastAPI(title="TriFrameBlog")
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
app.mount("/media", StaticFiles(directory=settings.UPLOAD_FOLDER), name="media")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(CSRFProtectMiddleware, csrf_secret=settings.CSRF_SECRET, enabled=not settings.TESTING)

manager.attach_middleware(app)

# Routes
app.include_router(accounts_router, prefix="/accounts", tags=["accounts"], include_in_schema=False)
app.include_router(blogs_router, prefix="", tags=["blogs"], include_in_schema=False)

# Admin
admin = Admin(
    async_engine,
    title="TriFrameBlog",
    index_view=AdminIndexView(label="Admin", path="/")
)
admin.add_view(BlogPostView(BlogPost))
admin.add_view(AdminView(Tag))
admin.add_view(EmailUserView(EmailUser))
admin.mount_to(app)

# Errors
@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    redirect_url = f"/accounts/login?next={request.url.path}"
    return RedirectResponse(url=redirect_url)