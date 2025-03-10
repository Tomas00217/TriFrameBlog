from flask import url_for
from flask_blog.accounts.models import EmailUser
from flask_blog.blogs.models import BlogPost
from flask_blog.extensions import db

def test_index_page(client, test_data):
    """Test that the index page loads successfully."""
    response = client.get(url_for("blogs.index"))

    assert response.status_code == 200

def test_index_contains_latest_three_blogs(client, test_data):
    """
    The index page contains only the latest three blogs.
    """
    response = client.get(url_for("blogs.index"))

    assert response.status_code == 200
    assert b"Blog4" not in response.data
    assert b"Blog5" in response.data
    assert b"Blog6" in response.data
    assert b"Blog7" in response.data

def test_index_contains_all_tags(client, test_data):
    """
    The index page contains all available tags.
    """
    response = client.get(url_for("blogs.index"))

    assert response.status_code == 200
    assert b"Food" in response.data
    assert b"Tech" in response.data

def test_blog_list_pagination_default(client, test_data):
    """Test pagination on the blogs page."""
    response = client.get(url_for("blogs.blogs"))

    assert response.status_code == 200
    assert b"Blog1" not in response.data
    assert b"Blog2" in response.data
    assert b"Blog3" in response.data
    assert b"Blog4" in response.data
    assert b"Blog5" in response.data
    assert b"Blog6" in response.data
    assert b"Blog7" in response.data

def test_blog_list_pagination_second_page(client, test_data):
    """Test pagination on the blogs page."""
    response = client.get(url_for("blogs.blogs", page=2))

    assert response.status_code == 200
    assert b"Blog1" in response.data
    assert b"Blog6" not in response.data
    assert b"Blog7" not in response.data

def test_blogs_filter_by_tag(client, test_data):
    """
    Filtering blogs by a tag returns only the blogs associated with that tag.
    """
    response = client.get(url_for("blogs.blogs", tag="tech"))

    assert response.status_code == 200
    assert b"Blog2" in response.data
    assert b"Blog7" in response.data
    assert b"Blog1" not in response.data
    assert b"Blog3" not in response.data

def test_blogs_search_function(client, test_data):
    """
    Searching for a blog by title returns the correct results.
    """
    response = client.get(url_for("blogs.blogs", search="search"))

    assert response.status_code == 200
    assert b"Blog1 search" in response.data
    assert b"Blog4 search" in response.data
    assert b"Blog2" not in response.data
    assert b"Blog5" not in response.data

def test_blog_detail_valid(client, test_data):
    """
    Detail page returns 200 status code for a valid blog.
    """
    blog = db.session.scalars(db.select(BlogPost)).first()
    response = client.get(url_for("blogs.detail", blog_id=blog.id))

    assert response.status_code == 200
    assert bytes(blog.title, "utf-8") in response.data

def test_blog_detail_invalid(client):
    """
    Detail page returns 404 status code for non-existing blog.
    """
    response = client.get(url_for("blogs.detail", blog_id=999))

    assert response.status_code == 404

def test_detail_contains_related_blogs(client, test_data):
    """
    Detail page shows related blogs by tags.
    """
    blog = db.session.execute(
        db.select(BlogPost).where(BlogPost.title == "Blog2")
    ).scalar_one()

    response = client.get(url_for("blogs.detail", blog_id=blog.id))

    assert response.status_code == 200
    assert b"Blog7" in response.data  # Blog7 also has "Tech" tag
    assert b"Blog1" not in response.data
    assert b"Blog3" not in response.data
    assert b"Blog4" not in response.data
    assert b"Blog5" not in response.data


def test_my_blogs_view_requires_login(client):
    """
    Unathenticated user is redirected to login.
    """
    response = client.get(url_for("blogs.my_blogs"))

    assert response.status_code == 302
    assert url_for("accounts.login") in response.headers["Location"]

def test_my_blogs_shows_user_blogs(logged_in_client):
    """
    Shows only blogs that belong to the user.
    """
    response = logged_in_client.get(url_for("blogs.my_blogs"))

    assert response.status_code == 200
    assert b"Blog1" in response.data
    assert b"Blog2" in response.data
    assert b"Blog3" not in response.data

def test_create_blog_requires_login(client):
    """
    Unathenticated user is redirected to login.
    """
    response = client.get(url_for("blogs.create"))

    assert response.status_code == 302
    assert url_for("accounts.login") in response.headers["Location"]

def test_create_blog(logged_in_client):
    """Test that a logged-in user can create a blog."""
    response = logged_in_client.post(url_for("blogs.create"), data={
        "title": "New Blog",
        "content": "This is a test blog",
        "tags": [1]
    })

    assert response.status_code == 302
    assert len(db.session.scalars(db.select(BlogPost)).all()) == 8

def test_edit_blog_requires_login(client):
    """
    Unathenticated user is redirected to login.
    """
    response = client.get(url_for("blogs.edit", blog_id=1))

    assert response.status_code == 302
    assert url_for("accounts.login") in response.headers["Location"]

def test_edit_blog_permission_denied(logged_in_client):
    """
    Authenticated user can edit only his own blogs, otherwise 403 status code is returned.
    """
    blog = db.session.execute(
        db.select(BlogPost).join(EmailUser).where(EmailUser.email == "test2@example.com")
    ).scalars().first()
    response = logged_in_client.get(url_for("blogs.edit", blog_id=blog.id))

    assert response.status_code == 403

def test_edit_blog(logged_in_client):
    """Test that a user can edit their own blog."""
    blog = db.session.scalars(db.select(BlogPost)).first()
    response = logged_in_client.post(url_for("blogs.edit", blog_id=blog.id), data={
        "title": "Updated Blog",
        "content": "Updated content",
        "tags": [1]
    })
    db.session.refresh(blog)

    assert response.status_code == 302
    assert blog.title == "Updated Blog"
    assert url_for("blogs.detail", blog_id=blog.id) in response.headers["Location"]

def test_delete_blog_requires_login(client):
    """
    Unathenticated user is redirected to login.
    """
    response = client.get(url_for("blogs.delete", blog_id=1))

    assert response.status_code == 302
    assert url_for("accounts.login") in response.headers["Location"]

def test_delete_blog_permission_denied(logged_in_client):
    """
    Authenticated user can delete only his own blogs, otherwise 403 status code is returned.
    """
    blog = db.session.execute(
        db.select(BlogPost).join(EmailUser).where(EmailUser.email == "test2@example.com")
    ).scalars().first()
    response = logged_in_client.get(url_for("blogs.delete", blog_id=blog.id))

    assert response.status_code == 403

def test_delete_blog(logged_in_client):
    """Test that a user can delete their own blog."""
    blog = db.session.scalars(db.select(BlogPost)).first()
    response = logged_in_client.post(url_for("blogs.delete", blog_id=blog.id))

    assert response.status_code == 302
    assert db.session.get(BlogPost, blog.id) is None
    assert url_for("blogs.my_blogs") in response.headers["Location"]