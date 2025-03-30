import asyncio
from fastapi_blog.blogs.models import BlogPost
from fastapi_blog.accounts.exceptions import EmailAlreadyExistsError
from fastapi_blog.services.email_user_service import EmailUserService
from fastapi_blog.database import async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi_blog.repositories.email_user_repository import get_email_user_repository
from fastapi_blog.services.email_user_service import EmailUserService, get_email_user_service
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

# Load superuser credentials from environment variables
SUPERUSER_EMAIL = "admin@blog.com"
SUPERUSER_PASSWORD = "admin"

async def create_superuser():
    """
    Creates a superuser if one does not already exist.
    """
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with Session() as session:
        try:
            email_user_repo = get_email_user_repository(session)
            user_service = get_email_user_service(email_user_repo)
            await user_service.create_user(
                email=SUPERUSER_EMAIL,
                password=SUPERUSER_PASSWORD,
                username="admin",
                is_active=True,
                is_staff=True,
            )
            print(f"Superuser {SUPERUSER_EMAIL} created successfully!")
        except EmailAlreadyExistsError:
            print(f"Superuser {SUPERUSER_EMAIL} already exists.")

if __name__ == "__main__":
    asyncio.run(create_superuser())