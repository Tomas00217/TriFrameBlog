import pytest
from shared.services.tag_service import TagService

@pytest.fixture
def mock_tag_repo(mocker):
    return mocker.Mock()

@pytest.fixture
def tag_service(mock_tag_repo):
    return TagService(mock_tag_repo)

def test_get_all_tags(tag_service, mock_tag_repo):
    """Test retrieving all tags"""
    mock_tag_repo.get_all.return_value = [
        {"id": 1, "name": "Python"},
        {"id": 2, "name": "Django"},
    ]

    result = tag_service.get_all()

    mock_tag_repo.get_all.assert_called_once()
    assert result == [
        {"id": 1, "name": "Python"},
        {"id": 2, "name": "Django"},
    ]