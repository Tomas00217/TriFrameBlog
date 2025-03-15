from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_blog.accounts.routes import accounts_router
from fastapi_blog.blogs.routes import blogs_router
from fastapi_blog.config import settings
from fastapi_blog.exceptions import NotAuthenticatedException
from fastapi_blog.auth import manager
from fastapi_blog.middleware import CSRFMiddleware

app = FastAPI(title="TriFrameBlog")

app.add_middleware(CSRFMiddleware)
manager.attach_middleware(app)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

app.include_router(accounts_router, prefix="/accounts", tags=["accounts"], include_in_schema=False)
app.include_router(blogs_router, prefix="", tags=["blogs"], include_in_schema=False)

@app.exception_handler(NotAuthenticatedException)
def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    redirect_url = f"/accounts/login?next={request.url.path}"
    return RedirectResponse(url=redirect_url)