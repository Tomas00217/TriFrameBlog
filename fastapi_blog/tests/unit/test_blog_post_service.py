import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from fastapi_blog.services.blog_post_service import BlogPostService
from fastapi_blog.blogs.exceptions import BlogPostNotFoundError

class MockBlogPost:
    def __init__(self, id=1, title="Test Blog", content="Test content", image="test.jpg", 
                 author=None, tags=None, created_at=None):
        self.id = id
        self.title = title
        self.content = content
        self.image = image
        self.author = author or MockEmailUser()
        self.tags = tags or []
        self.created_at = created_at or datetime.now()

class MockEmailUser:
    def __init__(self, id=1, email="test@example.com", username="testuser"):
        self.id = id
        self.email = email
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
    mock.get_recent = AsyncMock()
    mock.get_all_query = MagicMock()
    mock.get_paginated = AsyncMock()
    mock.get_by_id = AsyncMock()
    mock.get_related = AsyncMock()
    mock.get_by_author_query = MagicMock()
    mock.create = AsyncMock()
    mock.update = AsyncMock()
    mock.delete = AsyncMock()
    return mock

@pytest.fixture
def mock_tag_repo():
    mock = MagicMock()
    mock.get_by_ids = AsyncMock()
    return mock

@pytest.fixture
def mock_user_repo():
    mock = MagicMock()
    mock.get_by_id = AsyncMock()
    return mock

@pytest.fixture
def blog_post_service(mock_blog_repo, mock_tag_repo, mock_user_repo):
    service = BlogPostService(mock_blog_repo, mock_tag_repo, mock_user_repo)
    service.clean_content = MagicMock(side_effect=lambda x: x)
    service.upload_image = MagicMock(side_effect=lambda x: x if x else None)
    return service

@pytest.mark.asyncio
async def test_get_recent_blogs(blog_post_service, mock_blog_repo):
    """Test get_recent_blogs method"""
    limit = 3
    mock_blogs = [MockBlogPost(id=i) for i in range(1, limit+1)]
    mock_blog_repo.get_recent.return_value = mock_blogs

    result = await blog_post_service.get_recent_blogs(limit)

    mock_blog_repo.get_recent.assert_called_once_with(limit)
    assert result == mock_blogs
    assert len(result) == limit

@pytest.mark.asyncio
async def test_get_paginated_blogs(blog_post_service, mock_blog_repo):
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

    result = await blog_post_service.get_paginated_blogs(tag_slugs, search, page, per_page)

    mock_blog_repo.get_all_query.assert_called_once_with(tag_slugs, search)
    mock_blog_repo.get_paginated.assert_called_once_with(mock_query, page, per_page)
    assert result == mock_paginated
    assert len(result.items) == per_page

@pytest.mark.asyncio
async def test_get_blog_by_id_success(blog_post_service, mock_blog_repo):
    """Test get_blog_by_id when blog exists"""
    blog_id = 1
    mock_blog = MockBlogPost(id=blog_id)
    mock_blog_repo.get_by_id.return_value = mock_blog

    result = await blog_post_service.get_blog_by_id(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    assert result == mock_blog
    assert result.id == blog_id

@pytest.mark.asyncio
async def test_get_blog_by_id_not_found(blog_post_service, mock_blog_repo):
    """Test get_blog_by_id when blog does not exist"""
    blog_id = 999
    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(BlogPostNotFoundError):
        await blog_post_service.get_blog_by_id(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)

@pytest.mark.asyncio
async def test_get_related_blogs(blog_post_service, mock_blog_repo):
    """Test get_related_blogs method"""
    blog = MockBlogPost(id=1)
    limit = 3
    related_blogs = [MockBlogPost(id=i) for i in range(2, limit+2)]
    mock_blog_repo.get_related.return_value = related_blogs

    result = await blog_post_service.get_related_blogs(blog, limit)

    mock_blog_repo.get_related.assert_called_once_with(blog, limit=limit)
    assert result == related_blogs
    assert len(result) == limit

@pytest.mark.asyncio
async def test_get_paginated_user_blogs(blog_post_service, mock_blog_repo):
    """Test get_paginated_user_blogs method"""
    user = MockEmailUser()
    page = 1
    per_page = 6

    mock_query = MagicMock()
    mock_blog_repo.get_by_author_query.return_value = mock_query

    mock_blogs = [MockBlogPost(id=i, author=user) for i in range(1, per_page+1)]
    mock_paginated = MockPaginatedResult(mock_blogs, page, per_page, 10)
    mock_blog_repo.get_paginated.return_value = mock_paginated

    result = await blog_post_service.get_paginated_user_blogs(user, page, per_page)

    mock_blog_repo.get_by_author_query.assert_called_once_with(user)
    mock_blog_repo.get_paginated.assert_called_once_with(mock_query, page, per_page)
    assert result == mock_paginated
    assert len(result.items) == per_page

@pytest.mark.asyncio
async def test_create_blog_post(blog_post_service, mock_blog_repo, mock_tag_repo, mock_user_repo):
    """Test create_blog_post method"""
    title = "New Blog"
    content = "<p>Test content</p>"
    image = "test.jpg"
    author_id = 1
    tag_ids = [1, 2, 3]

    author = MockEmailUser(id=author_id)
    mock_user_repo.get_by_id.return_value = author

    tags = [MockTag(id=tid) for tid in tag_ids]
    mock_tag_repo.get_by_ids.return_value = tags

    new_blog = MockBlogPost(title=title, content=content, image=image, author=author, tags=tags)
    mock_blog_repo.create.return_value = new_blog

    result = await blog_post_service.create_blog_post(title, content, image, author_id, tag_ids)

    mock_user_repo.get_by_id.assert_called_once_with(author_id)
    blog_post_service.clean_content.assert_called_once_with(content)
    blog_post_service.upload_image.assert_called_once_with(image)
    mock_tag_repo.get_by_ids.assert_called_once_with(tag_ids)
    mock_blog_repo.create.assert_called_once()
    assert result == new_blog
    assert result.title == title
    assert result.content == content
    assert result.image == image
    assert result.author == author
    assert result.tags == tags

@pytest.mark.asyncio
async def test_update_blog_post(blog_post_service, mock_blog_repo, mock_tag_repo, mock_user_repo):
    """Test update_blog_post method"""
    blog_id = 1
    title = "Updated Blog"
    content = "<p>Updated content</p>"
    tag_ids = [2, 3]
    author_id = 1

    author = MockEmailUser(id=author_id)
    tags = [MockTag(id=tid) for tid in tag_ids]
    existing_blog = MockBlogPost(id=blog_id, author=author)
    updated_blog = MockBlogPost(id=blog_id, title=title, content=content, author=author, tags=tags)

    mock_blog_repo.get_by_id.return_value = existing_blog
    mock_tag_repo.get_by_ids.return_value = tags
    mock_blog_repo.update.return_value = updated_blog

    result = await blog_post_service.update_blog_post(blog_id=blog_id, title=title, content=content, tag_ids=tag_ids)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_tag_repo.get_by_ids.assert_called_once_with(tag_ids)
    blog_post_service.clean_content.assert_called_once_with(content)
    mock_blog_repo.update.assert_called_once()
    assert result == updated_blog
    assert result.id == blog_id
    assert result.title == title
    assert result.content == content
    assert result.tags == tags

@pytest.mark.asyncio
async def test_update_blog_post_not_found(blog_post_service, mock_blog_repo):
    """Test update_blog_post when blog does not exist"""
    blog_id = 999
    title = "Updated Blog"
    content = "<p>Updated content</p>"
    image = "updated.jpg"
    tag_ids = [2, 3]

    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(BlogPostNotFoundError):
        await blog_post_service.update_blog_post(blog_id, title, content, image, tag_ids)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_blog_repo.update.assert_not_called()

@pytest.mark.asyncio
async def test_update_blog_post_with_different_author(blog_post_service, mock_blog_repo, mock_tag_repo, mock_user_repo):
    """Test update_blog_post with a different author"""
    blog_id = 1
    title = "Updated Blog"
    content = "<p>Updated content</p>"
    tag_ids = [2, 3]
    old_author_id = 1
    new_author_id = 2

    old_author = MockEmailUser(id=old_author_id)
    new_author = MockEmailUser(id=new_author_id)
    tags = [MockTag(id=tid) for tid in tag_ids]
    existing_blog = MockBlogPost(id=blog_id, author=old_author)
    updated_blog = MockBlogPost(id=blog_id, title=title, content=content, author=new_author, tags=tags)

    mock_blog_repo.get_by_id.return_value = existing_blog
    mock_user_repo.get_by_id.return_value = new_author
    mock_tag_repo.get_by_ids.return_value = tags
    mock_blog_repo.update.return_value = updated_blog

    result = await blog_post_service.update_blog_post(blog_id=blog_id, title=title, content=content, tag_ids=tag_ids, author_id=new_author_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_user_repo.get_by_id.assert_called_once_with(new_author_id)
    mock_tag_repo.get_by_ids.assert_called_once_with(tag_ids)
    blog_post_service.clean_content.assert_called_once_with(content)
    mock_blog_repo.update.assert_called_once()
    assert result == updated_blog
    assert result.author == new_author

@pytest.mark.asyncio
async def test_update_blog_post_with_custom_date(blog_post_service, mock_blog_repo, mock_tag_repo):
    """Test update_blog_post with a custom creation date"""
    blog_id = 1
    title = "Updated Blog"
    content = "<p>Updated content</p>"
    tag_ids = [2, 3]
    custom_date = datetime(2023, 1, 1)

    author = MockEmailUser()
    tags = [MockTag(id=tid) for tid in tag_ids]
    existing_blog = MockBlogPost(id=blog_id, author=author)
    updated_blog = MockBlogPost(id=blog_id, title=title, content=content, author=author, tags=tags, created_at=custom_date)

    mock_blog_repo.get_by_id.return_value = existing_blog
    mock_tag_repo.get_by_ids.return_value = tags
    mock_blog_repo.update.return_value = updated_blog

    result = await blog_post_service.update_blog_post(blog_id=blog_id, title=title, content=content, tag_ids=tag_ids, created_at=custom_date)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_tag_repo.get_by_ids.assert_called_once_with(tag_ids)
    blog_post_service.clean_content.assert_called_once_with(content)
    mock_blog_repo.update.assert_called_once()
    assert result == updated_blog
    assert result.created_at == custom_date

@pytest.mark.asyncio
async def test_delete_blog_post(blog_post_service, mock_blog_repo):
    """Test delete_blog_post method"""
    blog_id = 1
    blog = MockBlogPost(id=blog_id)
    mock_blog_repo.get_by_id.return_value = blog
    mock_blog_repo.delete.return_value = None

    result = await blog_post_service.delete_blog_post(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_blog_repo.delete.assert_called_once_with(blog)
    assert result is None

@pytest.mark.asyncio
async def test_delete_blog_post_not_found(blog_post_service, mock_blog_repo):
    """Test delete_blog_post when blog does not exist"""
    blog_id = 999
    mock_blog_repo.get_by_id.return_value = None

    with pytest.raises(BlogPostNotFoundError):
        await blog_post_service.delete_blog_post(blog_id)

    mock_blog_repo.get_by_id.assert_called_once_with(blog_id)
    mock_blog_repo.delete.assert_not_called()

def test_upload_image_none(blog_post_service):
    """Test upload_image method with None input"""
    blog_post_service.upload_image = BlogPostService.upload_image.__get__(blog_post_service)

    result = blog_post_service.upload_image(None)

    assert result is None

@patch('html_sanitizer.Sanitizer.sanitize')
def test_clean_content(mock_sanitize, blog_post_service):
    """Test clean_content method using html-sanitizer"""
    blog_post_service.clean_content = BlogPostService.clean_content.__get__(blog_post_service)

    content = "<p>Test content</p><script>alert('XSS')</script>"
    cleaned_content = "<p>Test content</p>"
    mock_sanitize.return_value = cleaned_content

    result = blog_post_service.clean_content(content)

    mock_sanitize.assert_called_once()
    assert result == cleaned_content