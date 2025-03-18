from typing import Any
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi_blog.config import settings
from jinja2 import Environment, FileSystemLoader

def toast(request: Request, message: Any, type: str = "info"):
   if "_messages" not in request.session:
       request.session["_messages"] = []
       request.session["_messages"].append({"message": message, "type": type})

def get_toast_messages(request: Request):
   return request.session.pop("_messages") if "_messages" in request.session else []

jinja_env = Environment(
    loader=FileSystemLoader([str(path) for path in settings.TEMPLATES_DIRS]),
)
jinja_env.globals["get_toast_messages"] = get_toast_messages

templates = Jinja2Templates(env=jinja_env)