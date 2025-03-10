from datetime import datetime, timedelta, timezone
from flask_blog import create_app
from flask_blog.accounts.models import EmailUser
from flask_blog.blogs.models import BlogPost, Tag
from flask_blog.extensions import db
from flask_login import login_user
import pytest

@pytest.fixture(scope="function")
def app():
    """Create a new Flask app instance for each test."""
    app = create_app(testing=True)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Provides a test client for making requests."""
    return app.test_client()

@pytest.fixture(scope="function")
def test_data():
    """Seed test data before running a test."""
    user = EmailUser(email="test@example.com", password="password")
    user2 = EmailUser(email="test2@example.com", password="password")
    db.session.add_all([user, user2])
    db.session.commit()

    tag1 = Tag(name="Food")
    tag2 = Tag(name="Tech")

    base_time = datetime.now(timezone.utc)

    blog1 = BlogPost(title="Blog1 search", content="Content1", author_id=user.id, tags=[tag1], created_at=base_time)
    blog2 = BlogPost(title="Blog2", content="Content2", author_id=user.id, tags=[tag2], created_at=base_time + timedelta(seconds=1))
    blog3 = BlogPost(title="Blog3", content="Content3", author_id=user2.id, tags=[tag1], created_at=base_time + timedelta(seconds=2))
    blog4 = BlogPost(title="Blog4 search", content="Content4", author_id=user2.id, tags=[tag1], created_at=base_time + timedelta(seconds=3))
    blog5 = BlogPost(title="Blog5", content="Content5", author_id=user2.id, tags=[tag1], created_at=base_time + timedelta(seconds=4))
    blog6 = BlogPost(title="Blog6", content="Content6", author_id=user2.id, tags=[tag1], created_at=base_time + timedelta(seconds=5))
    blog7 = BlogPost(title="Blog7", content="Content7", author_id=user2.id, tags=[tag1, tag2], created_at=base_time + timedelta(seconds=6))

    db.session.add_all([tag1, tag2, blog1, blog2, blog3, blog4, blog5, blog6, blog7])
    db.session.commit()

    return user

@pytest.fixture
def logged_in_client(client, test_data):
    """Log in a user manually by modifying the session."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(test_data.id)

    return client