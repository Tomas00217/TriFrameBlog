from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker
from fastapi_blog.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = AsyncEngine(create_engine(url=settings.DATABASE_URL))

async def get_session():
    Session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with Session() as session:
        yield session

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)