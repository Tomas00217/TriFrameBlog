import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

settings = Settings()