from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from fastapi_blog.config import settings
from wtforms import Form
from wtforms.csrf.core import CSRF

serializer = URLSafeTimedSerializer(settings.CSRF_SECRET)

class ItsDangerousCSRF(CSRF):
    def setup_form(self, form):
        self.form_meta = form.meta
        return super().setup_form(form)
    
    def generate_csrf_token(self, csrf_token_field):
        return serializer.dumps("csrf-token")
    
    def validate_csrf_token(self, form, field):
        if not field.data:
            raise ValueError("CSRF token missing")
        
        try:
            value = serializer.loads(field.data, max_age=1800)
            if value != "csrf-token":
                raise ValueError("CSRF token invalid")
        except SignatureExpired:
            raise ValueError("CSRF token expired")
        except BadSignature:
            raise ValueError("CSRF token invalid")

class MyForm(Form):
    class Meta:
        csrf = True
        csrf_class = ItsDangerousCSRF