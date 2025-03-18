import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi_blog.services.tag_service import TagService

@pytest.fixture
def mock_tag_repo():
    """
    Creates a mock of the TagRepository with AsyncMock methods.
    """
    mock = MagicMock()
    mock.get_all = AsyncMock()
    return mock

@pytest.mark.asyncio
async def test_get_all_tags():
    """
    Tests that the get_all method retrieves all tags from the repository.
    """
    expected_tags = [{"id": 1, "name": "food"}, {"id": 2, "name": "tech"}]
    mock_repo = MagicMock()
    mock_repo.get_all = AsyncMock(return_value=expected_tags)

    service = TagService(mock_repo)

    result = await service.get_all()

    mock_repo.get_all.assert_called_once()
    assert result == expected_tags

@pytest.mark.asyncio
async def test_get_all_tags_empty_result():
    """
    Tests that the get_all method handles empty results properly.
    """
    mock_repo = MagicMock()
    mock_repo.get_all = AsyncMock(return_value=[])

    service = TagService(mock_repo)

    result = await service.get_all()

    mock_repo.get_all.assert_called_once()
    assert result == []
    assert isinstance(result, list)

@pytest.mark.asyncio
async def test_get_all_tags_propagates_exceptions():
    """
    Tests that exceptions from the repository are properly propagated.
    """
    mock_repo = MagicMock()
    mock_repo.get_all = AsyncMock(side_effect=Exception("Database error"))

    service = TagService(mock_repo)

    with pytest.raises(Exception) as excinfo:
        await service.get_all()

    assert "Database error" in str(excinfo.value)
    mock_repo.get_all.assert_called_once()