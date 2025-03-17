import os
from sqlmodel import SQLModel
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

test_engine = AsyncEngine(create_engine(url=TEST_DB_URL, connect_args={"check_same_thread": False}))
TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=test_engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_test_db():
    """Initialize the test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def cleanup_test_db():
    """Clean up the test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await test_engine.dispose()

    if os.path.exists("./test.db"):
        os.remove("./test.db")