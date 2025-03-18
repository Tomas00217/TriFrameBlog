import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from flask_blog.blogs.exceptions import BlogPostNotFoundError
from flask_blog.services.blog_post_service import BlogPostService

class MockBlogPost:
    def __init__(self, id=1, title="Test Blog", content="Test content", image="test.jpg", 
                 author=None, tags=None, created_at=None):
        self.id = id
        self.title = title
        self.content = content
        self.image = image
        self.author = author or MockUser()
        self.tags = tags or []
        self.created_at = created_at or datetime.now()

class MockUser:
    def __init__(self, id=1, username="testuser"):
        self.id = id
        self.username = username

class MockTag:
    def __init__(self, id=1, name="Test Tag", slug="test-tag"):
        self.id = id
        self.name = name
        self.slug = slug

class MockPaginatedResult:
    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page

@pytest.fixture
def mock_blog_repo():
    mock = MagicMock()
    return mock

@pytest.fixture
def mock_tag_repo():
    mock = MagicMock()
    return mock

@pytest.fixture
def blog_post_service(mock_blog_repo, mock_tag_repo):
    service = BlogPostService(mock_blog_repo, mock_tag_repo)
    service.clean_content = MagicMock(side_effect=lambda x: x)
    service.upload_image = MagicMock(side_effect=lambda x: x if x else None)
    return service

def test_get_recent_blogs(blog_post_service, mock_blog_repo):
    """Test get_recent_blogs method"""
    limit = 3
    mock_blogs = [MockBlogPost(id=i) for i in range(1, limit+1)]
    mock_blog_repo.get_recent.return_value = mock_blogs

    result = blog_post_service.get_recent_blogs(limit)

    mock_blog_repo.get_recent.assert_called_once_with(limit=limit)
    assert result == mock_blogs
    assert len(result) == limit

def test_get_paginated_blogs(blog_post_service, mock_blog_repo):
    """Test get_paginated_blogs method"""
    tag_slugs = ["tag1", "tag2"]
    search = "test"
    page = 1
    per_page = 10

    mock_query = MagicMock()
    mock_blog_repo.get_all_query.return_value = mock_query

    mock_blogs = [MockBlogPost(id=i) for i in range(1, per_page+1)]
    mock_paginated = MockPaginatedResult(mock_blogs, page, per_page, 15)
    mock_blog_repo.get_paginated.return_value = mock_paginated

    result = blog_post_service.get_paginated_blogs(tag_slugs, search, page, per_page)

    mock_blog_repo.get_all_query.assert_called_once_with(tag_slugs, search)
    mock_blog_repo.get_paginated.assert_called_once_with(mock_query, page, per_page)
    assert result == mock_paginated
    assert len(result.items) == per_page

def test_get_blog_by_id_success(blog_post_service, mock_blog_repo):
    """Test get_blog_by_id when blog exists"""
    blog_id = 1
    mock_blog = MockBlogPost(id=blog_id)
    mock_blog_repo.get_by_id.return_value = mock_blog

    result = blog_post_service.get_blog_by_id(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    assert result == mock_blog
    assert result.id == blog_id

def test_get_blog_by_id_not_found(blog_post_service, mock_blog_repo):
    """Test get_blog_by_id when blog does not exist"""
    blog_id = 999
    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(BlogPostNotFoundError, match="Blog post not found"):
        blog_post_service.get_blog_by_id(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)

def test_get_related_blogs(blog_post_service, mock_blog_repo):
    """Test get_related_blogs method"""
    blog = MockBlogPost(id=1)
    limit = 3
    related_blogs = [MockBlogPost(id=i) for i in range(2, limit+2)]
    mock_blog_repo.get_related.return_value = related_blogs

    result = blog_post_service.get_related_blogs(blog, limit)

    mock_blog_repo.get_related.assert_called_once_with(blog, limit=limit)
    assert result == related_blogs
    assert len(result) == limit

def test_get_user_blogs(blog_post_service, mock_blog_repo):
    """Test get_user_blogs method"""
    user = MockUser()
    mock_blogs = [MockBlogPost(id=i, author=user) for i in range(1, 4)]
    mock_blog_repo.get_by_author.return_value = mock_blogs

    result = blog_post_service.get_user_blogs(user)

    mock_blog_repo.get_by_author.assert_called_once_with(user)
    assert result == mock_blogs
    assert len(result) == 3

def test_get_paginated_user_blogs(blog_post_service, mock_blog_repo):
    """Test get_paginated_user_blogs method"""
    user = MockUser()
    page = 1
    per_page = 6

    mock_query = MagicMock()
    mock_blog_repo.get_by_author_query.return_value = mock_query

    mock_blogs = [MockBlogPost(id=i, author=user) for i in range(1, per_page+1)]
    mock_paginated = MockPaginatedResult(mock_blogs, page, per_page, 10)
    mock_blog_repo.get_paginated.return_value = mock_paginated

    result = blog_post_service.get_paginated_user_blogs(user, page, per_page)

    mock_blog_repo.get_by_author_query.assert_called_once_with(user)
    mock_blog_repo.get_paginated.assert_called_once_with(mock_query, page, per_page)
    assert result == mock_paginated
    assert len(result.items) == per_page

def test_get_all_blogs(blog_post_service, mock_blog_repo):
    """Test get_all_blogs method"""
    tag_slugs = ["tag1", "tag2"]
    search = "test"
    mock_blogs = [MockBlogPost(id=i) for i in range(1, 4)]
    mock_blog_repo.get_all.return_value = mock_blogs

    result = blog_post_service.get_all_blogs(tag_slugs, search)

    mock_blog_repo.get_all.assert_called_once_with(tag_slugs=tag_slugs, search=search)
    assert result == mock_blogs
    assert len(result) == 3

def test_create_blog_post(blog_post_service, mock_blog_repo, mock_tag_repo):
    """Test create_blog_post method"""
    title = "New Blog"
    content = "<p>Test content</p>"
    image = "test.jpg"
    author = MockUser()
    tag_ids = [1, 2, 3]

    tags = [MockTag(id=tid) for tid in tag_ids]
    mock_tag_repo.get_by_ids.return_value = tags

    new_blog = MockBlogPost(title=title, content=content, image=image, author=author, tags=tags)
    mock_blog_repo.create.return_value = new_blog

    result = blog_post_service.create_blog_post(title, content, image, author, tag_ids)

    blog_post_service.clean_content.assert_called_once_with(content)
    blog_post_service.upload_image.assert_called_once_with(image)
    mock_tag_repo.get_by_ids.assert_called_once_with(tag_ids)
    mock_blog_repo.create.assert_called_once_with(title, content, image, author, tags)
    assert result == new_blog
    assert result.title == title
    assert result.content == content
    assert result.image == image
    assert result.author == author
    assert result.tags == tags

def test_update_blog_post(blog_post_service, mock_blog_repo, mock_tag_repo):
    """Test update_blog_post method"""
    blog_id = 1
    title = "Updated Blog"
    content = "<p>Updated content</p>"
    image = "updated.jpg"
    tag_ids = [2, 3]

    author = MockUser()
    tags = [MockTag(id=tid) for tid in tag_ids]
    existing_blog = MockBlogPost(id=blog_id, author=author)
    updated_blog = MockBlogPost(id=blog_id, title=title, content=content, image=image, author=author, tags=tags)

    mock_blog_repo.get_by_id.return_value = existing_blog
    mock_tag_repo.get_by_ids.return_value = tags
    mock_blog_repo.update.return_value = updated_blog

    result = blog_post_service.update_blog_post(blog_id, title, content, image, tag_ids)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_tag_repo.get_by_ids.assert_called_once_with(tag_ids)
    blog_post_service.clean_content.assert_called_once_with(content)
    blog_post_service.upload_image.assert_called_once_with(image)
    mock_blog_repo.update.assert_called_once()
    assert result == updated_blog
    assert result.id == blog_id
    assert result.title == title
    assert result.content == content
    assert result.image == image
    assert result.tags == tags

def test_update_blog_post_not_found(blog_post_service, mock_blog_repo):
    """Test update_blog_post when blog does not exist"""
    blog_id = 999
    title = "Updated Blog"
    content = "<p>Updated content</p>"
    image = "updated.jpg"
    tag_ids = [2, 3]

    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(BlogPostNotFoundError, match="Blog post not found"):
        blog_post_service.update_blog_post(blog_id, title, content, image, tag_ids)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_blog_repo.update.assert_not_called()

def test_update_blog_post_without_image(blog_post_service, mock_blog_repo, mock_tag_repo):
    """Test update_blog_post without providing a new image"""
    blog_id = 1
    title = "Updated Blog"
    content = "<p>Updated content</p>"
    image = None
    original_image = "original.jpg"
    tag_ids = [2, 3]

    author = MockUser()
    tags = [MockTag(id=tid) for tid in tag_ids]
    existing_blog = MockBlogPost(id=blog_id, author=author, image=original_image)
    updated_blog = MockBlogPost(id=blog_id, title=title, content=content, image=original_image, author=author, tags=tags)

    mock_blog_repo.get_by_id.return_value = existing_blog
    mock_tag_repo.get_by_ids.return_value = tags
    mock_blog_repo.update.return_value = updated_blog

    result = blog_post_service.update_blog_post(blog_id, title, content, image, tag_ids)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_tag_repo.get_by_ids.assert_called_once_with(tag_ids)
    blog_post_service.clean_content.assert_called_once_with(content)
    blog_post_service.upload_image.assert_not_called()
    mock_blog_repo.update.assert_called_once()
    assert result == updated_blog
    assert result.image == original_image

def test_delete_blog_post(blog_post_service, mock_blog_repo):
    """Test delete_blog_post method"""
    blog_id = 1
    blog = MockBlogPost(id=blog_id)
    mock_blog_repo.get_by_id.return_value = blog
    mock_blog_repo.delete.return_value = None

    result = blog_post_service.delete_blog_post(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_blog_repo.delete.assert_called_once_with(blog)
    assert result is None

def test_delete_blog_post_not_found(blog_post_service, mock_blog_repo):
    """Test delete_blog_post when blog does not exist"""
    blog_id = 999
    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(BlogPostNotFoundError, match="Blog post not found"):
        blog_post_service.delete_blog_post(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_blog_repo.delete.assert_not_called()

@patch('cloudinary.uploader.upload')
def test_upload_image(mock_upload, blog_post_service):
    """Test upload_image method"""
    blog_post_service.upload_image = BlogPostService.upload_image.__get__(blog_post_service)

    image_file = "test_image.jpg"
    secure_url = "https://example.com/test_image.jpg"
    mock_upload.return_value = {"secure_url": secure_url}

    result = blog_post_service.upload_image(image_file)

    mock_upload.assert_called_once_with(image_file)
    assert result == secure_url

def test_upload_image_none(blog_post_service):
    """Test upload_image method with None input"""
    blog_post_service.upload_image = BlogPostService.upload_image.__get__(blog_post_service)

    result = blog_post_service.upload_image(None)

    assert result is None

@patch('bleach.clean')
def test_clean_content(mock_clean, blog_post_service):
    """Test clean_content method"""
    blog_post_service.clean_content = BlogPostService.clean_content.__get__(blog_post_service)

    content = "<p>Test content</p><script>alert('XSS')</script>"
    cleaned_content = "<p>Test content</p>"
    mock_clean.return_value = cleaned_content

    result = blog_post_service.clean_content(content)

    mock_clean.assert_called_once()
    assert result == cleaned_content

    args, kwargs = mock_clean.call_args
    assert kwargs['tags'] == ["h1", "h2", "h3", "p", "b", "i", "u", "a", "ul", "ol", "li", "br", "strong", "em", "span"]
    assert kwargs['attributes'] == {"a": ["href", "target"], "span": ["class", "contenteditable"]}