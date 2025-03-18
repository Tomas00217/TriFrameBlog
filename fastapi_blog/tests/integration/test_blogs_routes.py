from fastapi_blog.accounts.models import EmailUser
from fastapi_blog.blogs.models import BlogPost
import pytest
from sqlmodel import func, select
from tests.test_utils import TestingSessionLocal

@pytest.mark.asyncio
async def test_index_contains_latest_three_blogs(test_client):
    """Test the index route displays blogs correctly."""
    response = await test_client.get("/")

    assert response.status_code == 200

    assert "Blog4 search" not in response.text
    assert "Blog5" in response.text
    assert "Blog6" in response.text
    assert "Blog7" in response.text


@pytest.mark.asyncio
async def test_index_contains_latest_three_tags(test_client):
    """Test the index route displays tags correctly."""
    response = await test_client.get("/")

    assert response.status_code == 200

    assert "Food" in response.text
    assert "Tech" in response.text

@pytest.mark.asyncio
async def test_blog_list_pagination_default(test_client):
    """Test pagination on the blogs page."""
    response = await test_client.get("/blogs")

    assert response.status_code == 200
    assert "Blog1" not in response.text
    assert "Blog2" in response.text
    assert "Blog3" in response.text
    assert "Blog4" in response.text
    assert "Blog5" in response.text
    assert "Blog6" in response.text
    assert "Blog7" in response.text

@pytest.mark.asyncio
async def test_blog_list_pagination_second_page(test_client):
    """Test pagination on the blogs page."""
    response = await test_client.get("/blogs?page=2")

    assert response.status_code == 200
    assert "Blog1" in response.text
    assert "Blog6" not in response.text
    assert "Blog7" not in response.text

@pytest.mark.asyncio
async def test_blogs_filter_by_tag(test_client):
    """
    Filtering blogs by a tag returns only the blogs associated with that tag.
    """
    response = await test_client.get("/blogs?tag=tech")

    assert response.status_code == 200
    assert "Blog2" in response.text
    assert "Blog7" in response.text
    assert "Blog1" not in response.text
    assert "Blog3" not in response.text

@pytest.mark.asyncio
async def test_blogs_search_function(test_client):
    """
    Searching for a blog by title returns the correct results.
    """
    response = await test_client.get("/blogs?search=search")

    assert response.status_code == 200
    assert "Blog1 search" in response.text
    assert "Blog4 search" in response.text
    assert "Blog2" not in response.text
    assert "Blog5" not in response.text

@pytest.mark.asyncio
async def test_blog_detail_valid(test_client):
    """
    Detail page returns 200 status code for a valid blog.
    """
    response = await test_client.get(f"/blogs/1")

    assert response.status_code == 200
    assert "Blog1 search" in response.text

@pytest.mark.asyncio
async def test_blog_detail_invalid(test_client):
    """
    Detail page returns 404 status code for non-existing blog.
    """
    response = await test_client.get("/blogs/999")

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_detail_contains_related_blogs(test_client):
    """
    Detail page shows related blogs by tags.
    """
    response = await test_client.get("/blogs/2")

    assert response.status_code == 200
    assert "Blog7" in response.text  # Blog7 also has "Tech" tag
    assert "Blog1" not in response.text
    assert "Blog3" not in response.text
    assert "Blog4" not in response.text
    assert "Blog5" not in response.text

@pytest.mark.asyncio
async def test_my_blogs_view_requires_login(test_client):
    """
    Unathenticated user is redirected to login.
    """
    response = await test_client.get("blogs/my")

    assert response.status_code == 307
    assert "accounts/login" in response.headers["Location"]

@pytest.mark.asyncio
async def test_my_blogs_shows_user_blogs(auth_client):
    """
    Shows only blogs that belong to the user.
    """
    response = await auth_client.get("/blogs/my")

    assert response.status_code == 200
    assert "Blog1" in response.text
    assert "Blog2" in response.text
    assert "Blog3" not in response.text

@pytest.mark.asyncio
async def test_create_blog_requires_login(test_client):
    """
    Unathenticated user is redirected to login.
    """
    response = await test_client.get("/blogs/create")

    assert response.status_code == 307
    assert "accounts/login" in response.headers["Location"]

@pytest.mark.asyncio
async def test_create_blog(auth_client):
    """Test that a logged-in user can create a blog."""

    async with TestingSessionLocal() as session:
        initial_count = await session.scalar(select(func.count()).select_from(BlogPost))

    response = await auth_client.post(
        "/blogs/create",
        data={
            "title": "New Blog",
            "content": "This is a test blog",
            "tags": [1]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 303

    async with TestingSessionLocal() as session:
        new_count = await session.scalar(select(func.count()).select_from(BlogPost))

    assert new_count == initial_count + 1

@pytest.mark.asyncio
async def test_edit_blog_requires_login(test_client):
    """
    Unathenticated user is redirected to login.
    """
    response = await test_client.get("/blogs/1/edit")

    assert response.status_code == 307
    assert "accounts/login" in response.headers["Location"]

@pytest.mark.asyncio
async def test_edit_blog_permission_denied(auth_client):
    """
    Authenticated user can edit only his own blogs, otherwise 403 status code is returned.
    """

    async with TestingSessionLocal() as session:
        result = await session.exec(select(BlogPost).join(EmailUser).where(EmailUser.email == "test2@example.com"))
        blog = result.first()

    response = await auth_client.get(f"blogs/{blog.id}/edit")

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_edit_blog(auth_client):
    """Test that a logged-in user can create a blog."""
    async with TestingSessionLocal() as session:
        result = await session.exec(select(BlogPost).join(EmailUser).where(EmailUser.email == "test@example.com"))
        blog = result.first()

    response = await auth_client.post(
        f"/blogs/{blog.id}/edit",
        data={
            "title": "Updated Blog",
            "content": "This is an updated test blog",
            "tags": [1]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 303
    assert "blogs/my" in response.headers["Location"]

    async with TestingSessionLocal() as session:
        updated_blog = await session.get(BlogPost, blog.id)

    assert updated_blog.title == "Updated Blog"
    assert updated_blog.content == "This is an updated test blog"


@pytest.mark.asyncio
async def test_delete_blog_requires_login(test_client):
    """
    Unathenticated user is redirected to login.
    """
    response = await test_client.get("blogs/1/delete")

    assert response.status_code == 307
    assert "accounts/login" in response.headers["Location"]

@pytest.mark.asyncio
async def test_delete_blog_permission_denied(auth_client):
    """
    Authenticated user can delete only his own blogs, otherwise 403 status code is returned.
    """
    async with TestingSessionLocal() as session:
        result = await session.exec(select(BlogPost).join(EmailUser).where(EmailUser.email == "test2@example.com"))
        blog = result.first()

    response = await auth_client.get(f"blogs/{blog.id}/delete")

    assert response.status_code == 403

@pytest.mark.asyncio
async def test_delete_blog(auth_client):
    """Test that a user can delete their own blog."""
    async with TestingSessionLocal() as session:
        result = await session.exec(select(BlogPost).join(EmailUser).where(EmailUser.email == "test@example.com"))
        blog = result.first()

    response = await auth_client.post(f"blogs/{blog.id}/delete")

    assert response.status_code == 303

    async with TestingSessionLocal() as session:
        result = await session.exec(select(BlogPost).where(BlogPost.id == blog.id))
        deleted = result.first()

    assert deleted is None
    assert "blogs/my" in response.headers["Location"]