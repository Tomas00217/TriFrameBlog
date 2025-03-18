from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette_admin.contrib.sqlmodel import ModelView
from starlette_admin import CustomView
from starlette.status import HTTP_303_SEE_OTHER

class AdminIndexView(CustomView):
    async def render(self, request: Request, action: str | None = None) -> Response:
        if not request.state.user:
            return RedirectResponse(url="/accounts/login?next=/admin", status_code=HTTP_303_SEE_OTHER)

        return await super().render(request, action)

class AdminView(ModelView):
    def is_accessible(self, request: Request) -> bool:
        return request.state.user and request.state.user.is_staff