from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_blog.accounts.exceptions import EmailAlreadyExistsError
from fastapi_blog.accounts.forms import LoginForm, RegisterForm, UsernameUpdateForm
from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.auth import manager
from fastapi_blog.services.email_user_service import EmailUserService, get_email_user_service
from fastapi_blog.templating import templates, toast
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from starlette_wtf import csrf_protect

accounts_router = APIRouter()

@accounts_router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    next: str | None = None
):
    if request.state.user:
        toast(request, "You are already logged in.")
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

    form = await LoginForm.from_formdata(request)

    return templates.TemplateResponse(
        request, "login.html", {"form": form, "next": next})

@accounts_router.post("/login", response_class=HTMLResponse)
@csrf_protect
async def login(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)],
    next: Optional[str] = None
):
    try:
        form = await LoginForm.from_formdata(request)

        if await form.validate_on_submit():
            user = await user_service.get_user_by_email(form.email.data)

            if user and user.verify_password(form.password.data):
                access_token = manager.create_access_token(data={"sub": user.email})
                response = RedirectResponse(url=next or "/", status_code=HTTP_303_SEE_OTHER)
                manager.set_cookie(response, access_token)

                toast(request, "Login successful.", "success")
                return response
            else:
                form.email.errors.append("Your email and password did not match. Please try again.")

        return templates.TemplateResponse(request,
            "login.html", 
            {"form": form, "errors": form.errors},
            status_code=HTTP_400_BAD_REQUEST
        )
    except Exception:
        toast(request, "Error occured, please try again later.", "error")
        return templates.TemplateResponse(request,
            "login.html",
            {"form": form, "errors": form.errors},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )


@accounts_router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
):
    if request.state.user:
        toast(request, "You are already registered.")
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)

    form = await RegisterForm.from_formdata(request)

    return templates.TemplateResponse(
        request, "register.html", {"form": form})

@accounts_router.post("/register", response_class=HTMLResponse)
@csrf_protect
async def register(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)]
):
    try:
        form = await RegisterForm.from_formdata(request)

        if not await form.validate_on_submit():
            return templates.TemplateResponse(request,
                "register.html",
                {"form": form, "errors": form.errors},
                status_code=HTTP_400_BAD_REQUEST
            )

        await user_service.register_user(form.email.data, form.password1.data)

        toast(request, "Register successful.", "success")
        return RedirectResponse(url="/accounts/login", status_code=HTTP_303_SEE_OTHER)
    except EmailAlreadyExistsError as e:
        form.email.errors.append(e)
        return templates.TemplateResponse(request,
            "register.html",
            {"form": form, "errors": form.errors},
            status_code=HTTP_400_BAD_REQUEST
        )
    except Exception:
        toast(request, "Error occured, please try again later.", "error")
        return templates.TemplateResponse(request,
            "register.html",
            {"form": form, "errors": form.errors},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )

@accounts_router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse(url="/accounts/login")

    response.delete_cookie("auth_token")

    toast(request, "You were logged out.", "success")
    return response

@accounts_router.get("/profile")
async def profile_page(request: Request, user: Annotated[EmailUser, Depends(manager)]):
    form = await UsernameUpdateForm.from_formdata(request=request, obj=user)

    return templates.TemplateResponse(
        request, "profile.html", {"form": form})

@accounts_router.post("/profile", response_class=HTMLResponse)
@csrf_protect
async def profile(
    request: Request,
    user_service: Annotated[EmailUserService, Depends(get_email_user_service)],
    user: Annotated[EmailUser, Depends(manager)]
):
    try: 
        form = await UsernameUpdateForm.from_formdata(request)

        if not await form.validate_on_submit():
            return templates.TemplateResponse(request,
                "profile.html",
                {"form": form, "errors": form.errors},
                status_code=HTTP_400_BAD_REQUEST
            )

        await user_service.update_username(user, form.username.data)

        toast(request, "Your username has been updated!", "success")
        return RedirectResponse(url="/accounts/profile", status_code=HTTP_303_SEE_OTHER)
    except Exception:
        toast(request, "Error occured, please try again later.", "error")
        return templates.TemplateResponse(request,
            "profile.html",
            {"form": form, "errors": form.errors},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )