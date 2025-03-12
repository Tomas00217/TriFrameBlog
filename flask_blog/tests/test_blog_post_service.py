import pytest
from shared.services.blog_post_service import BlogPostService

@pytest.fixture
def mock_blog_repo(mocker):
    return mocker.Mock()

@pytest.fixture
def mock_tag_repo(mocker):
    return mocker.Mock()

@pytest.fixture
def blog_service(mock_blog_repo, mock_tag_repo):
    return BlogPostService(mock_blog_repo, mock_tag_repo)

def test_get_related_blogs(blog_service, mock_blog_repo):
    """Test retrieving related blogs based on tags"""
    mock_blog_repo.get_related.return_value = ["related_blog1", "related_blog2"]

    blog = {"id": 1, "title": "Main Blog"}
    result = blog_service.get_related_blogs(blog, limit=2)

    mock_blog_repo.get_related.assert_called_once_with(blog, limit=2)
    assert result == ["related_blog1", "related_blog2"]


def test_get_paginated_blogs(blog_service, mock_blog_repo):
    """Test retrieving paginated blogs"""
    mock_blog_repo.get_all_query.return_value = "query_stmt"
    mock_blog_repo.get_paginated.return_value = ["blog1", "blog2"]

    result = blog_service.get_paginated_blogs(tag_slugs=["tech"], search="Python", page=1, per_page=5)

    mock_blog_repo.get_all_query.assert_called_once_with(["tech"], "Python")
    mock_blog_repo.get_paginated.assert_called_once_with("query_stmt", 1, 5)
    assert result == ["blog1", "blog2"]


def test_get_user_blogs(blog_service, mock_blog_repo):
    """Test retrieving blogs written by a specific user"""
    mock_blog_repo.get_by_author.return_value = ["user_blog1", "user_blog2"]
    
    user = "test_user"
    result = blog_service.get_user_blogs(user)

    mock_blog_repo.get_by_author.assert_called_once_with(user)
    assert result == ["user_blog1", "user_blog2"]


def test_get_paginated_user_blogs(blog_service, mock_blog_repo):
    """Test retrieving paginated blogs for a specific user"""
    mock_blog_repo.get_by_author_query.return_value = "user_query_stmt"
    mock_blog_repo.get_paginated.return_value = ["user_blog1", "user_blog2"]

    user = "test_user"
    result = blog_service.get_paginated_user_blogs(user, page=2, per_page=4)

    mock_blog_repo.get_by_author_query.assert_called_once_with(user)
    mock_blog_repo.get_paginated.assert_called_once_with("user_query_stmt", 2, 4)
    assert result == ["user_blog1", "user_blog2"]


def test_get_recent_blogs(blog_service, mock_blog_repo):
    """Test retrieving recent blogs"""
    mock_blog_repo.get_recent.return_value = ["blog1", "blog2", "blog3"]

    result = blog_service.get_recent_blogs(limit=3)

    mock_blog_repo.get_recent.assert_called_once_with(limit=3)
    assert result == ["blog1", "blog2", "blog3"]


def test_get_blog_by_id_found(blog_service, mock_blog_repo):
    """Test retrieving a blog by ID when it exists"""
    mock_blog_repo.get_by_id.return_value = {"id": 1, "title": "Test Blog"}

    result = blog_service.get_blog_by_id(1)

    mock_blog_repo.get_by_id.assert_called_once_with(1)
    assert result == {"id": 1, "title": "Test Blog"}


def test_get_blog_by_id_not_found(blog_service, mock_blog_repo):
    """Test retrieving a blog by ID when it does not exist"""
    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Blog post not found"):
        blog_service.get_blog_by_id(1)

    mock_blog_repo.get_by_id.assert_called_once_with(1)


def test_get_all_blogs(blog_service, mock_blog_repo):
    """Test retrieving all blogs with optional filters"""
    mock_blog_repo.get_all.return_value = ["blog1", "blog2"]

    result = blog_service.get_all_blogs(tag_slugs=["tech"], search="Python")

    mock_blog_repo.get_all.assert_called_once_with(tag_slugs=["tech"], search="Python")
    assert result == ["blog1", "blog2"]


def test_create_blog_post(blog_service, mock_blog_repo, mock_tag_repo, mocker):
    """Test creating a new blog post"""
    mocker.patch.object(blog_service, "clean_content", return_value="cleaned content")
    mocker.patch.object(blog_service, "upload_image", return_value="image_url")
    mock_tag_repo.get_by_ids.return_value = ["tag1", "tag2"]

    mock_blog_repo.create.return_value = {"id": 1, "title": "New Blog"}

    result = blog_service.create_blog_post(
        title="New Blog",
        content="<p>Content</p>",
        image="image.jpg",
        author="user1",
        tag_ids=[1, 2]
    )

    blog_service.clean_content.assert_called_once_with("<p>Content</p>")
    blog_service.upload_image.assert_called_once_with("image.jpg")
    mock_tag_repo.get_by_ids.assert_called_once_with([1, 2])
    mock_blog_repo.create.assert_called_once_with(
        "New Blog", "cleaned content", "image_url", "user1", ["tag1", "tag2"]
    )
    assert result == {"id": 1, "title": "New Blog"}


def test_delete_blog_post_found(blog_service, mock_blog_repo):
    """Test deleting a blog post when it exists"""
    mock_blog_repo.get_by_id.return_value = {"id": 1, "title": "Test Blog"}

    blog_service.delete_blog_post(1)

    mock_blog_repo.get_by_id.assert_called_once_with(1)
    mock_blog_repo.delete.assert_called_once_with({"id": 1, "title": "Test Blog"})


def test_delete_blog_post_not_found(blog_service, mock_blog_repo):
    """Test deleting a blog post when it does not exist"""
    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Blog post not found"):
        blog_service.delete_blog_post(1)

    mock_blog_repo.get_by_id.assert_called_once_with(1)


def test_upload_image(mocker, blog_service):
    """Test image upload to Cloudinary"""
    mock_upload = mocker.patch("cloudinary.uploader.upload")
    mock_upload.return_value = {"secure_url": "https://cloudinary.com/image.jpg"}

    result = blog_service.upload_image("image_file")

    mock_upload.assert_called_once_with("image_file")
    assert result == "https://cloudinary.com/image.jpg"


def test_clean_content(blog_service):
    """Test HTML content cleaning"""
    dirty_content = '<script>alert("XSS")</script><p>Safe content</p>'
    cleaned_content = blog_service.clean_content(dirty_content)

    assert "<script>" not in cleaned_content
    assert "<p>Safe content</p>" in cleaned_content