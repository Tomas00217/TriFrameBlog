from fastapi_blog.database import async_engine
from fastapi_blog.config import settings
from fastapi_blog.exceptions import NotAuthenticatedException
from fastapi_blog.repositories.email_user_repository import EmailUserRepository
from fastapi_login import LoginManager
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


manager = LoginManager(
    settings.SECRET_KEY,
    "/accounts/login",
    cookie_name="auth_token",
    use_cookie=True,
    use_header=False,
    not_authenticated_exception=NotAuthenticatedException
)


@manager.user_loader()
async def load_user(email: str):
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with Session() as session:
        user_repo = EmailUserRepository(session)
        return await user_repo.get_by_email(email)