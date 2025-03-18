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
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_SECRET: str
    CLOUDINARY_API_KEY: str

    STATIC_DIR: Path = BASE_DIR.parent / "shared" / "static"

    TEMPLATES_DIRS: List[Path] = [
        BASE_DIR / "fastapi_blog" / "templates",
        BASE_DIR / "fastapi_blog" / "blogs" / "templates",
        BASE_DIR / "fastapi_blog" / "accounts" / "templates",
    ]

    model_config = ConfigDict(env_file=".env")

class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG: bool = True
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dev.db")
    CSRF_SECRET: str = os.getenv("CSRF_SECRET")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")

class TestingConfig(BaseConfig):
    """Testing configuration (used for pytest)."""

    DEBUG: bool = False
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    TESTING: bool = True

class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG: bool = False
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    CSRF_SECRET: str = os.getenv("CSRF_SECRET")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")

def get_settings():
    """Load the correct configuration based on the `FASTAPI_ENV` variable."""
    env = os.getenv("FASTAPI_ENV", "dev").lower()

    if env == "prod":
        return ProductionConfig(_env_file=".env.production")
    elif env == "test":
        return TestingConfig(_env_file=".env.test")
    
    return DevelopmentConfig(_env_file=".env")

settings = get_settings()