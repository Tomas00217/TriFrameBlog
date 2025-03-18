import pytest
from flask_login import current_user
from flask import url_for
from flask_blog.accounts.models import EmailUser
from flask_blog.extensions import db

@pytest.fixture
def registered_user():
    """
    Create and commit a test user.
    """
    user = EmailUser(email="user@example.com", password="password")
    db.session.add(user)
    db.session.commit()
    return user

def test_login_view(client, registered_user):
    """
    User login with valid credentials should be successful.
    """
    response = client.post(url_for("accounts.login"), data={
        "email": registered_user.email,
        "password": "password"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert "Login successful.".encode() in response.data
    assert current_user.is_authenticated

def test_login_invalid_credentials(client):
    """
    Login with invalid credentials should fail and show an error message.
    """
    response = client.post(url_for("accounts.login"), data={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })

    assert not current_user.is_authenticated
    assert response.status_code == 400
    assert "Your email and password did not match. Please try again.".encode() in response.data

def test_register_view(client):
    """
    User registration should create a new account and redirect to login.
    """
    response = client.post(url_for("accounts.register"), data={
        "email": "newuser@example.com", 
        "password1": "Testpassword123!", 
        "password2": "Testpassword123!"
    })

    assert EmailUser.query.filter_by(email="newuser@example.com").first() is not None
    assert response.status_code == 302
    assert url_for("accounts.login") in response.headers["Location"]

def test_register_passwords_dont_match(client):
    """
    Registration with mismatched passwords should fail.
    """
    response = client.post(url_for("accounts.register"), data={
        "email": "newuser@example.com",
        "password1": "Testpassword123!",
        "password2": "WrongSecondPass123."
    }, follow_redirects=True)

    assert EmailUser.query.filter_by(email="newuser@example.com").first() is None
    assert response.status_code == 400
    assert "Passwords must match".encode() in response.data

def test_register_email_exists(client, registered_user):
    """
    Registration with an existing email should fail.
    """
    response = client.post(url_for("accounts.register"), data={
        "email": registered_user.email,
        "password1": "Testpassword123!",
        "password2": "Testpassword123!"
    }, follow_redirects=True)

    assert response.status_code == 400
    assert "Email already registered".encode() in response.data

def test_profile_view_requires_login(client):
    """
    Unauthenticated user should be redirected to login page when accessing profile.
    """
    response = client.get(url_for("accounts.profile"))

    assert response.status_code == 302
    assert url_for("accounts.login") in response.headers["Location"]

def test_profile_update(logged_in_client, test_data):
    """
    Authenticated user should be able to update their username.
    """
    response = logged_in_client.post(url_for("accounts.profile"), data={"username": "updateduser"}, follow_redirects=True)

    db.session.refresh(test_data)
    assert test_data.username == "updateduser"
    assert response.status_code == 200