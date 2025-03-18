from fastapi_blog.accounts.models import EmailUser
import pytest
from sqlmodel import select
from tests.test_data import TEST_USER
from tests.test_utils import TestingSessionLocal


@pytest.mark.asyncio
async def test_login_view(test_client):
    """
    User login with valid credentials should be successful.
    """
    response = await test_client.post("accounts/login", data={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    })

    assert response.status_code == 303
    assert "auth_token" in response.cookies
    assert "/" in response.headers["Location"]

@pytest.mark.asyncio
async def test_login_invalid_credentials(test_client):
    """
    Login with invalid credentials should fail and show an error message.
    """
    response = await test_client.post("accounts/login", data={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }, follow_redirects=True)

    assert response.status_code == 400
    assert "Your email and password did not match. Please try again." in response.text

@pytest.mark.asyncio
async def test_register_view(test_client):
    """
    User registration should create a new account and redirect to login.
    """
    response = await test_client.post("accounts/register", data={
        "email": "newuser@example.com", 
        "password1": "Testpassword123!", 
        "password2": "Testpassword123!"
    })

    async with TestingSessionLocal() as session:
        result = await session.exec(select(EmailUser).where(EmailUser.email == "newuser@example.com"))
        new_user = result.first()

    assert new_user is not None
    assert response.status_code == 303
    assert "accounts/login" in response.headers["Location"]

@pytest.mark.asyncio
async def test_register_passwords_dont_match(test_client):
    """
    Registration with mismatched passwords should fail.
    """
    response = await test_client.post("accounts/register", data={
        "email": "newuser@example.com",
        "password1": "Testpassword123!",
        "password2": "WrongSecondPass123."
    }, follow_redirects=True)


    async with TestingSessionLocal() as session:
        result = await session.exec(select(EmailUser).where(EmailUser.email == "newuser@example.com"))
        new_user = result.first()

    assert new_user is None
    assert response.status_code == 400
    assert "Passwords must match" in response.text

@pytest.mark.asyncio
async def test_register_email_exists(test_client):
    """
    Registration with an existing email should fail.
    """
    response = await test_client.post("accounts/register", data={
        "email": TEST_USER["email"],
        "password1": "Testpassword123!",
        "password2": "Testpassword123!"
    }, follow_redirects=True)

    assert response.status_code == 400
    assert f"Email {TEST_USER["email"]} is already in use" in response.text

@pytest.mark.asyncio
async def test_profile_view_requires_login(test_client):
    """
    Unauthenticated user should be redirected to login page when accessing profile.
    """
    response = await test_client.get("accounts/profile")

    assert response.status_code == 307
    assert "accounts/login" in response.headers["Location"]

@pytest.mark.asyncio
async def test_profile_update(auth_client):
    """
    Authenticated user should be able to update their username.
    """
    response = await auth_client.post("accounts/profile",
        data={"username": "updateduser"},
        follow_redirects=True
    )

    async with TestingSessionLocal() as session:
        result = await session.exec(select(EmailUser).where(EmailUser.email == TEST_USER["email"]))
        updateduser = result.first()

    assert updateduser.username == "updateduser"
    assert response.status_code == 200
    assert "Your username has been updated!" in response.text