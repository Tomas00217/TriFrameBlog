import os

# Set environment variable BEFORE importing anything else
os.environ["FASTAPI_ENV"] = "test"

from fastapi_blog.repositories.email_user_repository import EmailUserRepository
from httpx import ASGITransport, AsyncClient
from fastapi_blog.database import get_session
from fastapi_blog.auth import load_user, manager
from fastapi_blog.main import app
import pytest_asyncio
from tests.test_data import TEST_USER, seed_test_data
from tests.test_utils import TestingSessionLocal, init_test_db, cleanup_test_db

async def override_get_session():
    """Override the database session for tests."""
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope="function")
async def setup_test_db():
    """Set up the test database and override dependencies."""
    await init_test_db()

    app.dependency_overrides[get_session] = override_get_session
    await seed_test_data()

    yield

    app.dependency_overrides = {}
    await cleanup_test_db()

@pytest_asyncio.fixture(scope="function")
async def test_client(setup_test_db):
    """Create a test client with the test database configured."""
    async with AsyncClient(
        base_url="http://testserver", 
        transport=ASGITransport(app=app)
        ) as async_client:
        yield async_client

async def test_load_user(email):
    """Test version of load_user using the test database session."""
    async with TestingSessionLocal() as session:
        user_repo = EmailUserRepository(session)
        return await user_repo.get_by_email(email)

@pytest_asyncio.fixture(scope="function")
async def override_auth():
    """Override the authentication user loader for tests."""
    manager._user_callback = test_load_user

    yield

    manager._user_callback = load_user

@pytest_asyncio.fixture(scope="function")
async def auth_client(setup_test_db, override_auth):
    """Create an authenticated test client."""
    async with AsyncClient(
        base_url="http://testserver", 
        transport=ASGITransport(app=app)
    ) as async_client:
        auth_token = manager.create_access_token(data={"sub": TEST_USER["email"]})
        async_client.cookies.set(manager.cookie_name, auth_token)

        yield async_client