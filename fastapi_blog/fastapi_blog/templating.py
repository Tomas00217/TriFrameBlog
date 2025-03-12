from fastapi.templating import Jinja2Templates
from fastapi_blog.config import settings

templates = Jinja2Templates(directory=[str(path) for path in settings.TEMPLATES_DIRS])
