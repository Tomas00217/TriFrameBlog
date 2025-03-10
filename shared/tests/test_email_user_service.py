import pytest
from shared.services.email_user_service import EmailUserService

@pytest.fixture
def mock_user_repo(mocker):
    return mocker.Mock()

@pytest.fixture
def email_user_service(mock_user_repo):
    return EmailUserService(mock_user_repo)


def test_register_user(email_user_service, mock_user_repo):
    """Test registering a new user"""
    mock_user_repo.create.return_value = {"id": 1, "email": "test@example.com"}

    result = email_user_service.register_user(email="test@example.com", password="securepassword")

    mock_user_repo.create.assert_called_once_with(email="test@example.com", password="securepassword")
    assert result == {"id": 1, "email": "test@example.com"}


def test_get_user_by_email_found(email_user_service, mock_user_repo):
    """Test retrieving a user by email when they exist"""
    mock_user_repo.get_by_email.return_value = {"id": 1, "email": "test@example.com"}

    result = email_user_service.get_user_by_email("test@example.com")

    mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    assert result == {"id": 1, "email": "test@example.com"}


def test_get_user_by_email_not_found(email_user_service, mock_user_repo):
    """Test retrieving a user by email when they do not exist"""
    mock_user_repo.get_by_email.return_value = None

    result = email_user_service.get_user_by_email("nonexistent@example.com")

    mock_user_repo.get_by_email.assert_called_once_with("nonexistent@example.com")
    assert result is None


def test_update_user(email_user_service, mock_user_repo, mocker):
    """Test updating a user's username"""
    user = mocker.Mock()
    user.username = "old_username"

    email_user_service.update_user(user, new_username="new_username")

    assert user.username == "new_username"
    mock_user_repo.update.assert_called_once_with(user)