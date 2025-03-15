from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.accounts.schemas import RegisterFormModel, UsernameUpdateForm, LoginForm
from fastapi_blog.auth import manager
from fastapi_blog.services.email_user_service import EmailUserService, get_email_user_service
from fastapi_blog.templating import templates
from starlette.status import HTTP_303_SEE_OTHER

accounts_router = APIRouter()

@accounts_router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    next: str | None = None
):
    return templates.TemplateResponse(
        "login.html", {"request": request, "next": next})

@accounts_router.post("/login")
async def login(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)],
    next: str | None = None
):
    form_data = await request.form()
    form_model, errors = await LoginForm.from_form_data(form_data)

    if errors:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "errors": errors,
                "values": dict(form_data)
            }
        )

    user = await user_service.get_user_by_email(form_model.email)

    if not user or not user.verify_password(form_model.password):
        errors = {"email": ["Your email and password did not match. Please try again."]}
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "errors": errors,
                "values": dict(form_data)
            }
        )

    access_token = manager.create_access_token(data={"sub": user.email})
    response = RedirectResponse(url=next or "/", status_code=HTTP_303_SEE_OTHER)
    manager.set_cookie(response, access_token)

    return response

@accounts_router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@accounts_router.post("/register")
async def register(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)],
):
    form_data = await request.form()
    form_model, errors = await RegisterFormModel.from_form_data(form_data)

    if errors:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request, 
                "errors": errors,
                "values": dict(form_data)
            }
        )

    user = await user_service.get_user_by_email(form_model.email)
    if user:
        errors = {"email": ["Email already registered"]}
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request, 
                "errors": errors,
                "values": dict(form_data)
            }
        )

    await user_service.register_user(form_model.email, form_model.password1)
    return RedirectResponse(url="/accounts/login", status_code=HTTP_303_SEE_OTHER)

@accounts_router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/accounts/login")

    response.delete_cookie("auth_token")

    return response

@accounts_router.get("/profile")
async def profile_page(request: Request, user: Annotated[EmailUser, Depends(manager)]):
    return templates.TemplateResponse("profile.html", {"request": request})

@accounts_router.post("/profile")
async def profile(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)],
    user: Annotated[EmailUser, Depends(manager)],
):
    form_data = await request.form()
    form_model, errors = await UsernameUpdateForm.from_form_data(form_data)

    if errors:
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request, 
                "errors": errors,
                "values": dict(form_data)
            }
        )

    await user_service.update_user(user, form_model.username)
    return RedirectResponse(url="/accounts/profile", status_code=HTTP_303_SEE_OTHER)
