from typing import Annotated
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_blog.accounts.forms import LoginForm, RegisterForm, UsernameUpdateForm
from fastapi_blog.auth import manager
from fastapi_blog.services.email_user_service import EmailUserService, get_email_user_service
from fastapi_blog.templating import templates
from starlette.status import HTTP_303_SEE_OTHER

accounts_router = APIRouter()

@accounts_router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
):
    form = LoginForm()

    return templates.TemplateResponse(
        "login.html", {"request": request, "form": form})

@accounts_router.post("/login")
async def login(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)]
):
    form = LoginForm(await request.form())

    if form.validate():
        user = await user_service.get_user_by_email(form.email.data)

        if user and user.verify_password(form.password.data):
            access_token = manager.create_access_token(data={"sub": user.email})
            response = RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
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
    form = RegisterForm()

    return templates.TemplateResponse(
        "register.html", {"request": request, "form": form})

@accounts_router.post("/register")
async def register(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)]
):
    form = RegisterForm(await request.form())

    if not await form.validate(user_service):
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
async def profile_page(request: Request):
    form = UsernameUpdateForm(obj=request.state.user)

    return templates.TemplateResponse(
        "profile.html", {"request": request, "form": form})

@accounts_router.post("/profile")
async def profile(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)]
):
    form = UsernameUpdateForm(await request.form())

    if not form.validate():
        return templates.TemplateResponse("profile.html",
            {"request": request, "form": form, "errors": form.errors}
        )

    await user_service.update_user(request.state.user, form.username.data)
    return RedirectResponse(url="/accounts/profile", status_code=HTTP_303_SEE_OTHER)
