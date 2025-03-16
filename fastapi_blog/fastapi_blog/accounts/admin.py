from datetime import datetime, timezone
from fastapi_blog.accounts.exceptions import EmailAlreadyExistsError
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.admin import AdminView
from fastapi_blog.database import async_engine
from fastapi_blog.repositories.email_user_repository import get_email_user_repository
from fastapi_blog.services.email_user_service import get_email_user_service
from starlette_admin import PasswordField
from starlette.requests import Request
from typing import Any, Dict
from starlette_admin.exceptions import FormValidationError
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

class EmailUserView(AdminView):
    model = EmailUser
    identity = "email-user"
    name = "User"
    label = "Users"
    icon = "users"

    fields = ["id", "email", "username", PasswordField("password"), "is_active", "is_staff", "created_at"]
    
    exclude_fields_from_list = ["password_hash", "password"]
    exclude_fields_from_detail = ["password_hash", "password"]
    exclude_fields_from_create = ["id", "password_hash"]
    exclude_fields_from_edit = ["id", "password_hash"]

    async def get_user_service(self):
        Session = sessionmaker(
            bind=async_engine, class_=AsyncSession, expire_on_commit=False
        )
        async with Session() as session:
            email_user_repo = get_email_user_repository(session)
            user_service = get_email_user_service(email_user_repo)
            return user_service

    async def validate_data(self, data: Dict, is_create: bool = True):
        errors = {}

        if is_create and not data.get("password"):
            errors["password"] = "Password is required"

        if not data.get("email"):
            errors["email"] = "Email is required"

        if len(errors) > 0:
            raise FormValidationError(errors)

    async def create(self, request: Request, data: Dict) -> Dict[str, Any]:
        try:
            user_service = await self.get_user_service()

            await self.validate_data(data)

            email = data.get("email")
            username = data.get("username")
            password = data.get("password")
            is_active = data.get("is_active", True)
            is_staff = data.get("is_staff", False)
            created_at = datetime.now(timezone.utc).replace(tzinfo=None)

            user = await user_service.create_user(
                email=email,
                password=password,
                username=username,
                is_active=is_active,
                is_staff=is_staff,
                created_at=created_at
            )

            return user
        except EmailAlreadyExistsError as e:
            raise FormValidationError({"email": e})
        except Exception as e:
            raise e

    async def edit(self, request: Request, pk: Any, data: Dict) -> Dict[str, Any]:
        try:
            user_service = await self.get_user_service()

            await self.validate_data(data, False)

            email = data.get("email")
            username = data.get("username")
            is_active = data.get("is_active")
            is_staff = data.get("is_staff")
            password = data.get("password", None)

            updated_user = await user_service.update_user(
                user_id=int(pk),
                email=email,
                password=password if password else None,
                username=username,
                is_active=is_active,
                is_staff=is_staff
            )

            return updated_user
        except EmailAlreadyExistsError as e:
            raise FormValidationError({"email": e})
        except Exception as e:
            raise e