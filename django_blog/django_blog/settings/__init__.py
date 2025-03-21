import os
from dotenv import load_dotenv

environment = os.environ.get('DJANGO_ENV', 'development')

env_file = f".env.{environment}" if environment != 'development' else ".env"
load_dotenv(env_file)

if environment == 'production':
    from .production import *
elif environment == 'testing':
    from .testing import *
else:
    from .development import *