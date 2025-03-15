from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_blog.accounts.forms import LoginForm, RegisterForm, UsernameUpdateForm
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.auth import manager
from fastapi_blog.services.email_user_service import EmailUserService, get_email_user_service
from fastapi_blog.templating import templates
from starlette.status import HTTP_303_SEE_OTHER
from starlette_wtf import csrf_protect

accounts_router = APIRouter()

@accounts_router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    next: str | None = None
):
    form = await LoginForm.from_formdata(request)

    return templates.TemplateResponse(
        "login.html", {"request": request, "form": form, "next": next})

@accounts_router.post("/login")
@csrf_protect
async def login(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)],
    next: str | None = None
):
    form = await LoginForm.from_formdata(request)

    if await form.validate_on_submit():
        user = await user_service.get_user_by_email(form.email.data)

        if user and user.verify_password(form.password.data):
            access_token = manager.create_access_token(data={"sub": user.email})
            response = RedirectResponse(url=next or "/", status_code=HTTP_303_SEE_OTHER)
            manager.set_cookie(response, access_token)

            return response
        else:
            form.email.errors.append("Your email and password did not match. Please try again.")
        
    return templates.TemplateResponse("login.html", 
        {"request": request, "form": form, "errors": form.errors}
    )

@accounts_router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
):
    form = await RegisterForm.from_formdata(request)

    return templates.TemplateResponse(
        "register.html", {"request": request, "form": form})

@accounts_router.post("/register")
@csrf_protect
async def register(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)]
):
    form = await RegisterForm.from_formdata(request)

    if not await form.validate(user_service=user_service):
        return templates.TemplateResponse("register.html",
            {"request": request, "form": form, "errors": form.errors}
        )

    await user_service.register_user(form.email.data, form.password1.data)
    return RedirectResponse(url="/accounts/login", status_code=HTTP_303_SEE_OTHER)

@accounts_router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/accounts/login")

    response.delete_cookie("auth_token")

    return response

@accounts_router.get("/profile")
async def profile_page(request: Request, user: Annotated[EmailUser, Depends(manager)]):
    form = await UsernameUpdateForm.from_formdata(request=request, obj=user)

    return templates.TemplateResponse(
        "profile.html", {"request": request, "form": form})

@accounts_router.post("/profile")
@csrf_protect
async def profile(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    form = await UsernameUpdateForm.from_formdata(request)

    if not await form.validate_on_submit():
        return templates.TemplateResponse("profile.html",
            {"request": request, "form": form, "errors": form.errors}
        )

    await user_service.update_user(user, form.username.data)
    return RedirectResponse(url="/accounts/profile", status_code=HTTP_303_SEE_OTHER)
