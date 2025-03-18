from datetime import datetime, timezone
import pytest
from unittest.mock import MagicMock
from flask_blog.accounts.exceptions import EmailAlreadyExistsError
from flask_blog.services.email_user_service import EmailUserService

class MockEmailUser:
    def __init__(self, id=1, email="test@example.com", username=None, 
                 is_active=True, is_staff=False, created_at=None):
        self.id = id
        self.email = email
        self.username = username
        self.is_active = is_active
        self.is_staff = is_staff
        self.created_at = created_at or datetime.now(timezone.utc).replace(tzinfo=None)
        self.password = "hashed_password"

    def set_password(self, password):
        self.password = f"hashed_{password}"

@pytest.fixture
def mock_user_repo():
    """
    Creates a mock of the UserRepository.
    """
    mock = MagicMock()
    return mock

@pytest.fixture
def email_user_service(mock_user_repo):
    """
    Creates an EmailUserService instance with a mock repository.
    """
    return EmailUserService(mock_user_repo)

def test_get_user_by_email_when_user_exists(email_user_service, mock_user_repo):
    """
    Tests get_user_by_email when the user exists.
    """
    email = "test@example.com"
    mock_user = MockEmailUser(email=email)
    mock_user_repo.get_by_email.return_value = mock_user

    result = email_user_service.get_user_by_email(email)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    assert result == mock_user
    assert result.email == email

def test_get_user_by_email_when_user_does_not_exist(email_user_service, mock_user_repo):
    """
    Tests get_user_by_email when the user does not exist.
    """
    email = "nonexistent@example.com"
    mock_user_repo.get_by_email.return_value = None

    result = email_user_service.get_user_by_email(email)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    assert result is None

def test_register_user_successful(email_user_service, mock_user_repo):
    """
    Tests register_user when registration is successful.
    """
    email = "new@example.com"
    password = "password123"
    mock_user = MockEmailUser(email=email)
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = mock_user

    result = email_user_service.register_user(email, password)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.create.assert_called_once_with(email=email, password=password)
    assert result == mock_user
    assert result.email == email

def test_register_user_email_already_exists(email_user_service, mock_user_repo):
    """
    Tests register_user when the email already exists.
    """
    email = "existing@example.com"
    password = "password123"
    mock_user = MockEmailUser(email=email)
    mock_user_repo.get_by_email.return_value = mock_user

    with pytest.raises(EmailAlreadyExistsError) as exc_info:
        email_user_service.register_user(email, password)

    assert email in str(exc_info.value)
    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.create.assert_not_called()

def test_update_user(email_user_service, mock_user_repo):
    """
    Tests updating a user's username.
    """
    user = MockEmailUser()
    user.username = "old_username"

    email_user_service.update_user(user, new_username="new_username")

    assert user.username == "new_username"
    mock_user_repo.update.assert_called_once_with(user)