import pytest
from unittest.mock import MagicMock
from flask_blog.services.tag_service import TagService

@pytest.fixture
def mock_tag_repo():
    """
    Creates a mock of the TagRepository.
    """
    mock = MagicMock()
    return mock

@pytest.fixture
def tag_service(mock_tag_repo):
    """
    Creates an TagService instance with a mock repository.
    """
    return TagService(mock_tag_repo)

def test_get_all_tags(tag_service, mock_tag_repo):
    """
    Tests that the get_all method retrieves all tags from the repository.
    """
    expected_tags = [{"id": 1, "name": "Food"}, {"id": 2, "name": "Tech"}]
    mock_tag_repo.get_all.return_value = expected_tags

    result = tag_service.get_all()

    mock_tag_repo.get_all.assert_called_once()
    assert result == expected_tags

def test_get_all_tags_empty_result(tag_service, mock_tag_repo):
    """
    Tests that the get_all method handles empty results properly.
    """
    mock_tag_repo.get_all.return_value = []

    result = tag_service.get_all()

    mock_tag_repo.get_all.assert_called_once()
    assert result == []
    assert isinstance(result, list)

def test_get_all_tags_propagates_exceptions(tag_service, mock_tag_repo):
    """
    Tests that exceptions from the repository are properly propagated.
    """
    mock_tag_repo.get_all.side_effect = Exception("Database error")

    with pytest.raises(Exception) as excinfo:
        tag_service.get_all()

    assert "Database error" in str(excinfo.value)
    mock_tag_repo.get_all.assert_called_once()