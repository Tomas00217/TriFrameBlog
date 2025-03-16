import importlib
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    STATIC_DIR: Path = BASE_DIR.parent / "shared" / "static"
    CSRF_SECRET: str = os.getenv("CSRF_SECRET")

    TEMPLATES_DIRS: List[Path] = [
        BASE_DIR / "fastapi_blog" / "templates",
        BASE_DIR / "fastapi_blog" / "blogs" / "templates",
        BASE_DIR / "fastapi_blog" / "accounts" / "templates",
    ]

settings = Settings()