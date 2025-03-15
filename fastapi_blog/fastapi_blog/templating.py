from typing import Any
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi_blog.config import settings

def toast(request: Request, message: Any, type: str = "info"):
   if "_messages" not in request.session:
       request.session["_messages"] = []
       request.session["_messages"].append({"message": message, "type": type})

def get_toast_messages(request: Request):
   return request.session.pop("_messages") if "_messages" in request.session else []

templates = Jinja2Templates(directory=[str(path) for path in settings.TEMPLATES_DIRS])
templates.env.globals["get_toast_messages"] = get_toast_messages