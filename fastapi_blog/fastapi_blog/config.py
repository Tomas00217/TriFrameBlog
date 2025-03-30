import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig(BaseSettings):
    """Base configuration (shared by all environments)."""

    DATABASE_URL: str
    SECRET_KEY: str = "default_secret"
    DEBUG: bool = False
    CSRF_SECRET: str
    TESTING: bool = False

    USE_CLOUDINARY: bool = False

    STATIC_DIR: Path = BASE_DIR.parent / "shared" / "static"

    UPLOAD_FOLDER: Path = BASE_DIR / "media"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = ['.jpg', '.jpeg', '.png']

    TEMPLATES_DIRS: List[Path] = [
        BASE_DIR / "fastapi_blog" / "templates",
        BASE_DIR / "fastapi_blog" / "blogs" / "templates",
        BASE_DIR / "fastapi_blog" / "accounts" / "templates",
    ]

    model_config = ConfigDict(env_file=".env", extra="allow")

class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG: bool = True
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")
    CSRF_SECRET: str = os.getenv("CSRF_SECRET")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    USE_CLOUDINARY: bool = False

class TestingConfig(BaseConfig):
    """Testing configuration (used for pytest)."""

    DEBUG: bool = True
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    TESTING: bool = True
    CSRF_SECRET: str = os.getenv("CSRF_SECRET", "test_csrf_secret")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "test_secret_key")
    USE_CLOUDINARY: bool = False

class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG: bool = False
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    CSRF_SECRET: str = os.getenv("CSRF_SECRET")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    USE_CLOUDINARY: bool = os.getenv("USE_CLOUDINARY", "True").lower() == "true"
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")

def get_settings():
    """Load the correct configuration based on the `FASTAPI_ENV` variable."""
    env = os.getenv("FASTAPI_ENV", "dev").lower()

    config_map = {
        "prod": ProductionConfig,
        "test": TestingConfig,
        "dev": DevelopmentConfig
    }

    config_class = config_map.get(env, DevelopmentConfig)
    env_file = f".env.{env}" if env != "dev" else ".env"

    # Explicitly load only the specific env file
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file, override=True)

    return config_class()

settings = get_settings()