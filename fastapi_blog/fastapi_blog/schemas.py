from typing import Dict, Optional
from fastapi.datastructures import FormData
from fastapi_blog.config import settings
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pydantic import BaseModel, Field, field_validator


serializer = URLSafeTimedSerializer(settings.CSRF_SECRET)

class CSRFFormModel(BaseModel):
    csrf_token: str = Field(...)
    
    @field_validator('csrf_token')
    @classmethod
    def validate_csrf_token(cls, v: str) -> str:
        try:
            value = serializer.loads(v, max_age=1800)
            if value != "csrf-token":
                raise ValueError("CSRF token invalid")
        except SignatureExpired:
            raise ValueError("CSRF token expired")
        except BadSignature:
            raise ValueError("CSRF token invalid")
        return v
    
    @classmethod
    async def from_form_data(cls, form_data: FormData) -> tuple[Optional['CSRFFormModel'], Optional[Dict[str, list[str]]]]:
        data_dict = dict(form_data)

        try:
            return cls(**data_dict), None
        except Exception as e:

            errors = {}
            if hasattr(e, 'errors'):
                for error in e.errors():
                    if 'loc' in error and error['loc'] and len(error['loc']) > 0:
                        field = error['loc'][0]
                    else:
                        field = '_form'

                    if field not in errors:
                        errors[field] = []

                    error_msg = error['msg']
                    if error_msg.startswith("Value error, "):
                        error_msg = error_msg[13:]

                    errors[field].append(error_msg)

            return None, errors
