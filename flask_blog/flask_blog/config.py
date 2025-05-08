import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

config_name = os.environ.get("FLASK_ENV", "development")

if config_name == "development":
    env_file = BASE_DIR / ".env"
else:
    env_file = BASE_DIR / f".env.{config_name}"

if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URI"]
    SQLALCHEMY_ENGINE_OPTIONS = {"future": True}
    FLASK_ADMIN_SWATCH = "cerulean"

    STATIC_FOLDER = BASE_DIR.parent / 'shared' / 'static'

    UPLOAD_FOLDER = BASE_DIR / 'media'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    USE_LOCAL_STORAGE = True

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    USE_LOCAL_STORAGE = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    WTF_CSRF_ENABLED = False
    USE_LOCAL_STORAGE = True

class ProductionConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USE_LOCAL_STORAGE = False

    cloudinary.config(
        cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
        api_key=os.environ["CLOUDINARY_API_KEY"],
        api_secret=os.environ["CLOUDINARY_API_SECRET"],
        secure=True
    )

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig, 
    'production': ProductionConfig,
    'default': DevelopmentConfig
}