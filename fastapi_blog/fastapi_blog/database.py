from sqlmodel import SQLModel, create_engine, Session
from fastapi_blog.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)