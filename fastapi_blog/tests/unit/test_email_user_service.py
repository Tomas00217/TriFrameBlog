import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

from fastapi_blog.services.email_user_service import EmailUserService
from fastapi_blog.accounts.exceptions import EmailAlreadyExistsError

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
    Creates a mock of the EmailUserRepository with AsyncMock methods.
    """
    mock = MagicMock()
    mock.get_by_id = AsyncMock()
    mock.get_by_email = AsyncMock()
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    return mock

@pytest.fixture
def email_user_service(mock_user_repo):
    """
    Creates an EmailUserService instance with a mock repository.
    """
    return EmailUserService(mock_user_repo)

@pytest.mark.asyncio
async def test_get_user_by_id_when_user_exists(email_user_service, mock_user_repo):
    """
    Tests get_user_by_id when the user exists.
    """
    user_id = 1
    mock_user = MockEmailUser(id=user_id)
    mock_user_repo.get_by_id.return_value = mock_user

    result = await email_user_service.get_user_by_id(user_id)

    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    assert result == mock_user
    assert result.id == user_id

@pytest.mark.asyncio
async def test_get_user_by_id_when_user_does_not_exist(email_user_service, mock_user_repo):
    """
    Tests get_user_by_id when the user does not exist.
    """
    user_id = 999
    mock_user_repo.get_by_id.return_value = None

    result = await email_user_service.get_user_by_id(user_id)

    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    assert result is None

@pytest.mark.asyncio
async def test_get_user_by_email_when_user_exists(email_user_service, mock_user_repo):
    """
    Tests get_user_by_email when the user exists.
    """
    email = "test@example.com"
    mock_user = MockEmailUser(email=email)
    mock_user_repo.get_by_email.return_value = mock_user

    result = await email_user_service.get_user_by_email(email)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    assert result == mock_user
    assert result.email == email

@pytest.mark.asyncio
async def test_get_user_by_email_when_user_does_not_exist(email_user_service, mock_user_repo):
    """
    Tests get_user_by_email when the user does not exist.
    """
    email = "nonexistent@example.com"
    mock_user_repo.get_by_email.return_value = None

    result = await email_user_service.get_user_by_email(email)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    assert result is None

@pytest.mark.asyncio
async def test_register_user_successful(email_user_service, mock_user_repo):
    """
    Tests register_user when registration is successful.
    """
    email = "new@example.com"
    password = "password123"
    mock_user = MockEmailUser(email=email)
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = mock_user

    result = await email_user_service.register_user(email, password)

    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.create.assert_called_once_with(email=email, password=password)
    assert result == mock_user
    assert result.email == email

@pytest.mark.asyncio
async def test_register_user_email_already_exists(email_user_service, mock_user_repo):
    """
    Tests register_user when the email already exists.
    """
    email = "existing@example.com"
    password = "password123"
    mock_user = MockEmailUser(email=email)
    mock_user_repo.get_by_email.return_value = mock_user

    with pytest.raises(EmailAlreadyExistsError) as exc_info:
        await email_user_service.register_user(email, password)

    assert email in str(exc_info.value)
    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.create.assert_not_called()

@pytest.mark.asyncio
async def test_create_user_successful(email_user_service, mock_user_repo):
    """
    Tests create_user when creation is successful.
    """
    email = "new@example.com"
    password = "password123"
    username = "newuser"
    is_active = True
    is_staff = False
    created_at = datetime.now(timezone.utc).replace(tzinfo=None)

    mock_user = MockEmailUser(email=email, username=username, 
                             is_active=is_active, is_staff=is_staff,
                             created_at=created_at)
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = mock_user

    result = await email_user_service.create_user(
        email=email, 
        password=password, 
        username=username, 
        is_active=is_active, 
        is_staff=is_staff, 
        created_at=created_at
    )

    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.create.assert_called_once_with(
        email, password, username, is_active, is_staff, created_at
    )
    assert result == mock_user
    assert result.email == email
    assert result.username == username
    assert result.is_active == is_active
    assert result.is_staff == is_staff
    assert result.created_at == created_at

@pytest.mark.asyncio
async def test_create_user_email_already_exists(email_user_service, mock_user_repo):
    """
    Tests create_user when the email already exists.
    """
    email = "existing@example.com"
    password = "password123"
    mock_user = MockEmailUser(email=email)
    mock_user_repo.get_by_email.return_value = mock_user

    with pytest.raises(EmailAlreadyExistsError) as exc_info:
        await email_user_service.create_user(email, password)

    assert email in str(exc_info.value)
    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.create.assert_not_called()

@pytest.mark.asyncio
async def test_update_user_successful(email_user_service, mock_user_repo):
    """
    Tests update_user when update is successful.
    """
    user_id = 1
    email = "updated@example.com"
    password = "newpassword"
    username = "updateduser"
    is_active = False
    is_staff = True

    mock_user = MockEmailUser(id=user_id)
    mock_user_repo.get_by_id.return_value = mock_user
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.update.return_value = MockEmailUser(
        id=user_id, email=email, username=username, 
        is_active=is_active, is_staff=is_staff
    )

    result = await email_user_service.update_user(
        user_id=user_id,
        email=email,
        password=password,
        username=username,
        is_active=is_active,
        is_staff=is_staff
    )

    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.update.assert_called_once()
    assert result.id == user_id
    assert result.email == email
    assert result.username == username
    assert result.is_active == is_active
    assert result.is_staff == is_staff

@pytest.mark.asyncio
async def test_update_user_not_found(email_user_service, mock_user_repo):
    """
    Tests update_user when the user is not found.
    """
    user_id = 999
    mock_user_repo.get_by_id.return_value = None

    with pytest.raises(ValueError) as exc_info:
        await email_user_service.update_user(user_id, email="new@example.com")

    assert str(user_id) in str(exc_info.value)
    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    mock_user_repo.update.assert_not_called()

@pytest.mark.asyncio
async def test_update_user_email_already_exists(email_user_service, mock_user_repo):
    """
    Tests update_user when the new email already exists for another user.
    """
    user_id = 1
    email = "existing@example.com"

    mock_user = MockEmailUser(id=user_id, email="original@example.com")
    mock_user_repo.get_by_id.return_value = mock_user

    existing_user = MockEmailUser(id=2, email=email)
    mock_user_repo.get_by_email.return_value = existing_user

    with pytest.raises(EmailAlreadyExistsError) as exc_info:
        await email_user_service.update_user(user_id, email=email)

    assert email in str(exc_info.value)
    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    mock_user_repo.get_by_email.assert_called_once_with(email)
    mock_user_repo.update.assert_not_called()

@pytest.mark.asyncio
async def test_update_user_same_email(email_user_service, mock_user_repo):
    """
    Tests update_user when the email remains the same.
    """
    user_id = 1
    email = "same@example.com"

    mock_user = MockEmailUser(id=user_id, email=email)
    mock_user_repo.get_by_id.return_value = mock_user
    mock_user_repo.update.return_value = mock_user

    result = await email_user_service.update_user(user_id, email=email)

    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    mock_user_repo.get_by_email.assert_not_called()
    mock_user_repo.update.assert_called_once()
    assert result.email == email

@pytest.mark.asyncio
async def test_update_user_partial_update(email_user_service, mock_user_repo):
    """
    Tests update_user when only some fields are updated.
    """
    user_id = 1
    username = "newusername"

    mock_user = MockEmailUser(id=user_id, username="oldusername")
    mock_user_repo.get_by_id.return_value = mock_user

    updated_user = MockEmailUser(id=user_id, username=username)
    mock_user_repo.update.return_value = updated_user

    result = await email_user_service.update_user(user_id, username=username)

    mock_user_repo.get_by_id.assert_called_once_with(user_id)
    mock_user_repo.update.assert_called_once()
    assert result.username == username

@pytest.mark.asyncio
async def test_update_username(email_user_service, mock_user_repo):
    """
    Tests update_username function.
    """
    user = MockEmailUser(username="oldusername")
    new_username = "newusername"

    updated_user = MockEmailUser(username=new_username)
    mock_user_repo.update.return_value = updated_user

    result = await email_user_service.update_username(user, new_username)

    assert user.username == new_username
    mock_user_repo.update.assert_called_once_with(user)
    assert result.username == new_username