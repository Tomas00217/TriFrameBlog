from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_blog.accounts.routes import accounts_router
from fastapi_blog.blogs.routes import blogs_router
from fastapi_blog.config import settings
from fastapi_blog.exceptions import NotAuthenticatedException
from fastapi_blog.auth import manager
from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import CSRFProtectMiddleware

app = FastAPI(title="TriFrameBlog")
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware(CSRFProtectMiddleware, csrf_secret=settings.CSRF_SECRET)

manager.attach_middleware(app)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
app.include_router(blogs_router, prefix="", tags=["blogs"])

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    redirect_url = f"/accounts/login?next={request.url.path}"
    return RedirectResponse(url=redirect_url)