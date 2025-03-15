from fastapi import Request
from fastapi_blog.config import settings
from itsdangerous import URLSafeTimedSerializer
from starlette.middleware.base import BaseHTTPMiddleware

serializer = URLSafeTimedSerializer(settings.CSRF_SECRET)

class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.csrf_token = serializer.dumps("csrf-token")

        response = await call_next(request)
        return response